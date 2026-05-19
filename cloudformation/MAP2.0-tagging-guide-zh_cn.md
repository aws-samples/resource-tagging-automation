# MAP 2.0 Core Service 自动化打标签指南

本指南将 AWS MAP（Migration Acceleration Program）2.0 对 Core Service 的标签规范，与本仓库 `resource-tagging-automation` 的自动化方案打通：读者按本指南操作，即可在拿到 MPE 号后**一次性部署**，让此后所有新建的 Core Service 资源被自动打上 `map-migrated` 标签，无需逐个资源手工处理。

---

## 1. 适用范围

**适用：** 本仓库 Lambda 自动覆盖以下 17 类 AWS Core Service 资源——EC2、ELB、EFS、EBS、S3、RDS、DynamoDB、Lambda、OpenSearch、ElastiCache、Redshift、SageMaker、SNS、SQS、KMS、MQ、MSK、ECS。

**不适用：**
- **Bedrock 推理资源**：系统预定义 Model 无法直接打 Tag，必须经由 Application Inference Profile 这一独立链路，参见原始 docx 操作指南。
- **账户中已存在的旧资源**：本方案只覆盖**新建**资源，存量资源请到 [AWS Tag Editor](https://console.aws.amazon.com/resource-groups/tag-editor/find-resources) 批量补打。

> **提示：** 哪些服务可以计算 MAP credit、哪些不能，请向对应 BD/MBD 确认。本方案只解决"标签打得上"的工程问题，不替你判断"算不算 credit"。

---

## 2. MAP 2.0 标签规范

CSS（MAP 计费引擎）对 Core Service 标签的要求只有两步：

1. 拿到 **MPE<XXXXX>** 号后，激活 `map-migrated` 标签（在账单控制台的 Cost Allocation Tags 中激活）。
2. 用「前缀 + XXXXX 数字字符」作为标签 Value 打到资源上。

### 标签 Key/Value 格式

| 场景 | Key | Value 示例 |
|---|---|---|
| 通用迁移 | `map-migrated` | `migXXXXXABCD` |
| SAP 迁移 | `map-migrated` | `sapXXXXXABCD` |

### 不需要做的事

- ❌ **不需要** 激活 CUR（Cost & Usage Report）和其它标签。
- ❌ **不需要** 在 Migration Hub 中生成 Server ID。
- ❌ Tag Value **不需要** 以 `PE-` 开头。

---

## 3. 前置准备

- 已通过 MAP 申请并拿到 **MPE 号**（例如 `migXXXXXABCD`）。
- 已配置 AWS CLI v2 凭证（如选择 CLI 部署）：`aws configure`，并设置目标区域 `AWS_REGION`。
- 拥有部署 CloudFormation 栈、创建 IAM 角色与 Lambda 函数的权限。

---

## 4. 部署方案：一键打标签

下载本仓库的 CloudFormation 模版 `cloudformation/resource-tagging-automation.yaml`，二选一执行下列任一方式即可。

### 方式 A：AWS Console

1. 打开 AWS Console → CloudFormation → **Create Stack**。
2. **Upload a template file**，上传 `resource-tagging-automation.yaml`。
3. **Stack name** 输入 `map2-auto-tagging`。
4. 参数配置：

    | 参数 | 取值 |
    |---|---|
    | `AutomationTags` | `{"map-migrated":"migXXXXXABCD"}`（替换为真实 MPE 号） |
    | 其余参数 | 保持默认 |

5. 勾选 **I acknowledge that AWS CloudFormation might create IAM resources.**，点击 **Create stack**。
6. 等待 3–5 分钟完成。

### 方式 B：AWS CLI（推荐自动化场景与 AI Agent）

```bash
aws cloudformation deploy \
  --stack-name map2-auto-tagging \
  --template-file cloudformation/resource-tagging-automation.yaml \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides \
    AutomationTags='{"map-migrated":"migXXXXXABCD"}'
```

如需同时打 MAP 标签与团队/环境标签：

```bash
aws cloudformation deploy \
  --stack-name map2-auto-tagging \
  --template-file cloudformation/resource-tagging-automation.yaml \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides \
    AutomationTags='{"map-migrated":"migXXXXXABCD","Owner":"team-a","Env":"prod"}'
```

如账号已存在记录管理事件的 CloudTrail，可复用现有桶避免重复 Trail：

```bash
... \
  --parameter-overrides \
    AutomationTags='{"map-migrated":"migXXXXXABCD"}' \
    TrailS3Bucket=my-existing-cloudtrail-bucket
```

---

## 5. 验证

```bash
# 1) 等待栈部署完成
aws cloudformation wait stack-create-complete --stack-name map2-auto-tagging

# 2) 创建一个测试 S3 桶
aws s3 mb s3://map2-tag-test-$(date +%s)

# 3) 几秒后查看桶上的标签
aws s3api get-bucket-tagging --bucket map2-tag-test-<刚才的时间戳>
```

预期输出中应包含：

```json
{ "TagSet": [{"Key": "map-migrated", "Value": "migXXXXXABCD"}] }
```

也可以登录 AWS Console，进入 [Tag Editor](https://console.aws.amazon.com/resource-groups/tag-editor/find-resources)，按 `map-migrated` 过滤，确认新建资源都已被打上标签。

如需排查 Lambda 行为，进入 Lambda → `resource-tagging-automation-function` → **Monitor** 查看调用次数与日志，正常情况下会输出形如 `tagging for new S3...` 的日志。

---

## 6. 修改或切换 MPE 号

不需要重新部署整个栈，直接更新 Lambda 环境变量即可。修改后再创建的资源会按新值打标签；**已存在的资源不会被回填**。

```bash
aws lambda update-function-configuration \
  --function-name resource-tagging-automation-function \
  --environment '{"Variables":{"tags":"{\"map-migrated\":\"migNEWVALUE\"}"}}'
```

> **注意：** Lambda 内部对该环境变量执行 `json.loads`，因此双引号必须转义。

---

## 7. 历史资源补打标签

本方案不会回填存量资源。请到 [AWS Tag Editor](https://console.aws.amazon.com/resource-groups/tag-editor/find-resources) 控制台：

1. 选定区域和资源类型（可勾选"All supported resource types"）。
2. 搜索后选中目标资源。
3. 在 **Manage tags of selected resources** 中加上 `map-migrated = migXXXXXABCD`。

---

## 8. 常见问题与注意事项

- **资源没被打上标签？** 依次检查：
  1. CloudFormation 栈是否成功创建（`aws cloudformation describe-stacks --stack-name map2-auto-tagging`）。
  2. CloudTrail 是否在持续记录管理事件。
  3. EventBridge 规则 `resource-tagging-automation-rules` 是否触发（控制台的 Monitoring 里有 Invocations 指标）。
  4. Lambda 函数是否报错（CloudWatch Logs）。

- **覆盖范围只包含模版里显式列出的事件源**（见 `cloudformation/resource-tagging-automation.yaml` 中 EventBridge Rule 的 EventPattern），如需扩展到其它服务，请参考根目录 `README.md` 的 *Support more resources* 一节。

- **中国区（cn-north-1 / cn-northwest-1）支持** ：Lambda 内置 ARN 转换函数 `transfromArn4CN`，自动把 `arn:aws:` 替换为 `arn:aws-cn:`，无需额外配置。

- **多标签共存**：在 `AutomationTags` 里写入完整 JSON 即可，对象中除 `map-migrated` 外再追加业务标签即可一并打上。

---

## 参考

- 本仓库 CloudFormation 部署文档：[`cloudformation/README-zh_cn.md`](../cloudformation/README-zh_cn.md)
- 项目根说明：[`../README.md`](../README.md)
- 架构图：![架构图](../docs/architecture.png)
