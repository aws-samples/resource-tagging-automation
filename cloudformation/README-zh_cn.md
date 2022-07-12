### 准备：
1. 下载CloudFormation模版 resource-tagging-automation.yaml
2. AWS 账号

### 架构图：
![ProjectArchitecture](../docs/architecture.png)

### 部署：
1. 打开AWS Console， 导航到CloudFormation，
2. 点击Create Stack，
3. 点击“Upload a template file”，选择下载到本地的CloudFormation 模版，
4. 在“Stack name”输入名称，
5. 参数部分设置，
    A. AutomationTags : 以json的形式输入自动为每个资源打的Tag， 如： {"tag1": "test1","tag2": "test2"}
    B. EventBridgeRuleName ： 输入EventBridge Rule的名称， 默认： resource-tagging-automation-rules
    C. IAMAutoTaggingPolicyName ：输入创建的IAM customed managed policy的名称， 默认： resource-tagging-automation-policy
    D. IAMAutoTaggingRoleName ：输入为Lambda创建的角色名称， 默认： resource-tagging-automation-role
    E. LambdaAutoTaggingFunctionName ：输入lambda函数的名称， 默认： resource-tagging-automation-function
6. 点击Next， 勾选“I acknowledge that AWS CloudFormation might create IAM resources.”， 点击“Create stack”，
7. Stackset需要3-5分钟完成。

### 修改tag标签：
1. 到Lambda 控制界面， 选择Lambda函数， 默认： resource-tagging-automation-function，
2. 到Configuration Tab， 选择 Environment variables， 点击Edit 修改tags标签的值，
3. 修改值 （json格式）， 点击Save。 那么之后资源被创建的时候会被打上新的tag。
