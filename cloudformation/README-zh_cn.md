## 资源自动打标签 — CloudFormation 部署

本目录提供 CloudFormation 模版，用于部署资源自动打标签方案。该方案支持为新创建的 EC2、ELB、EFS、EBS、S3、RDS、DynamoDB、Lambda、OpenSearch、ElastiCache、Redshift、SageMaker、SNS、SQS、KMS、MQ、MSK 和 ECS 资源自动打上标签。

### 准备
1. 下载 CloudFormation 模版 `resource-tagging-automation.yaml`。
2. AWS 账号。

### 架构图
![ProjectArchitecture](../docs/architecture.png)

### 部署
1. 打开 AWS Console，导航到 CloudFormation。
2. 点击 **Create Stack**。
3. 点击 **Upload a template file**，选择下载到本地的 CloudFormation 模版。
4. 在 **Stack name** 输入栈名称。
5. 配置参数：

    | 参数 | 默认值 | 说明 |
    |---|---|---|
    | `AutomationTags` | _(空)_ | 自动为每个资源打上的标签，JSON 对象格式，例如：`{"TagName1": "TagValue1","TagName2": "TagValue2"}` |
    | `LambdaAutoTaggingFunctionName` | `resource-tagging-automation-function` | Lambda 函数名称 |
    | `EventBridgeRuleName` | `resource-tagging-automation-rules` | EventBridge 规则名称 |
    | `IAMAutoTaggingRoleName` | `resource-tagging-automation-role` | Lambda 使用的 IAM 角色名称 |
    | `IAMAutoTaggingPolicyName` | `resource-tagging-automation-policy` | IAM 自定义托管策略名称 |
    | `TrailName` | `resource-tagging-automation-trail` | 本栈创建的多区域 CloudTrail 名称 |
    | `TrailS3Bucket` | _(空)_ | 用于存放 CloudTrail 日志的现有 S3 桶名称。留空则自动创建名为 `tagging-log-<stack-suffix>` 的桶 |

6. 点击 **Next**，勾选 **I acknowledge that AWS CloudFormation might create IAM resources.**，然后点击 **Create stack**。
7. 栈创建通常需要 3–5 分钟完成。

### 通过 AWS CLI 部署（适用于 AI Agent）

**Claude Code**、**Qiro-CLI** 等 AI 编程 Agent 可以使用 AWS CLI 直接完成端到端部署，无需打开 AWS Console。前置条件：已安装 AWS CLI v2、已配置凭证（`aws configure` 或 `AWS_PROFILE`）、已设置目标区域（`AWS_REGION` 或 `--region`）。

1. 在 `cloudformation/` 目录下执行部署命令：

    ```bash
    aws cloudformation deploy \
      --stack-name resource-tagging-automation \
      --template-file resource-tagging-automation.yaml \
      --capabilities CAPABILITY_IAM \
      --parameter-overrides \
        AutomationTags='{"TagName1":"TagValue1","TagName2":"TagValue2"}'
    ```

   如需覆盖更多参数，可继续以 `Key=Value` 形式追加，例如：`TrailS3Bucket=my-existing-log-bucket TrailName=my-trail`。

2. 等待部署完成并验证 Lambda 已就绪：

    ```bash
    aws cloudformation wait stack-create-complete --stack-name resource-tagging-automation
    aws lambda get-function --function-name resource-tagging-automation-function \
      --query 'Configuration.[FunctionName,State,LastUpdateStatus]'
    ```

3. 后续修改标签时无需重新部署整个栈：

    ```bash
    aws lambda update-function-configuration \
      --function-name resource-tagging-automation-function \
      --environment '{"Variables":{"tags":"{\"Owner\":\"team-a\",\"Env\":\"prod\"}"}}'
    ```

4. 拆除部署（自动创建的 CloudTrail 桶保留策略为 Retain，如不再需要请手动删除）：

    ```bash
    aws cloudformation delete-stack --stack-name resource-tagging-automation
    aws cloudformation wait stack-delete-complete --stack-name resource-tagging-automation
    ```

**给 AI Agent 的提示：**
- Lambda 环境变量 `tags` 必须是 JSON 编码后的**字符串**（函数内部会调用 `json.loads`），因此第 3 步中需要对引号进行转义。
- 若账号已有记录管理事件的 CloudTrail，建议传入 `TrailS3Bucket=<已有桶名>`，让本栈复用现有桶，避免创建重复 Trail。
- 参数较多时，可以将覆盖项写入文件，使用 `--parameter-overrides file://params.json` 传入。文件内容为 JSON 数组，例如：`[{"ParameterKey":"AutomationTags","ParameterValue":"{\"Owner\":\"team-a\"}"}]`。

### 说明
- 本栈创建的 CloudTrail 启用多区域，并包含全局服务事件。
- 当 `TrailS3Bucket` 留空时，将创建一个名为 `tagging-log-<stack-suffix>` 的新 S3 桶，`DeletionPolicy` 设置为 `Retain`。删除栈**不会**自动删除该桶，若不再需要日志请手动清理。
- 当 `TrailS3Bucket` 指向现有桶时，不会创建新桶；需要自行确保桶策略允许 `cloudtrail.amazonaws.com` 对相应前缀执行 `s3:GetBucketAcl` 与 `s3:PutObject`。

### 修改 tag
1. 进入 Lambda 控制台，选择 Lambda 函数（默认：`resource-tagging-automation-function`）。
2. 切换到 **Configuration** 标签页，选择 **Environment variables**，点击 **Edit** 修改 `tags` 环境变量的值。
3. 修改值（JSON 格式）后点击 **Save**。之后新创建的资源将被自动打上新标签。
