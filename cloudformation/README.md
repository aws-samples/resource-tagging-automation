## Resource Tagging Automation — CloudFormation Deployment

This directory provides the CloudFormation template that deploys the auto-tagging solution. It supports tagging newly created EC2, ELB, EFS, EBS, S3, RDS, DynamoDB, Lambda, OpenSearch, ElastiCache, Redshift, SageMaker, SNS, SQS, KMS, MQ, MSK and ECS resources.

### Prepare
1. Download the CloudFormation template `resource-tagging-automation.yaml`.
2. An AWS account.

### Architecture
![ProjectArchitecture](../docs/architecture.png)

### Deployment
1. Open the AWS Console, navigate to CloudFormation.
2. Click **Create Stack**.
3. Click **Upload a template file**, select the CloudFormation template downloaded locally.
4. Enter a name in **Stack name**.
5. Configure the parameters:

    | Parameter | Default | Description |
    |---|---|---|
    | `AutomationTags` | _(empty)_ | Tags applied to every newly created resource, as a JSON object, e.g. `{"TagName1": "TagValue1","TagName2": "TagValue2"}` |
    | `LambdaAutoTaggingFunctionName` | `resource-tagging-automation-function` | Name of the Lambda function |
    | `EventBridgeRuleName` | `resource-tagging-automation-rules` | Name of the EventBridge rule |
    | `IAMAutoTaggingRoleName` | `resource-tagging-automation-role` | IAM role name attached to the Lambda |
    | `IAMAutoTaggingPolicyName` | `resource-tagging-automation-policy` | IAM custom managed policy name |
    | `TrailName` | `resource-tagging-automation-trail` | Name of the multi-region CloudTrail created by this stack |
    | `TrailS3Bucket` | _(empty)_ | Existing S3 bucket name for CloudTrail logs. Leave blank to auto-create a bucket named `tagging-log-<stack-suffix>` |

6. Click **Next**, check **I acknowledge that AWS CloudFormation might create IAM resources.**, then click **Create stack**.
7. The stack typically takes 3–5 minutes to finish.

### Notes
- The CloudTrail created by this stack is multi-region and includes global service events.
- When `TrailS3Bucket` is left blank, a new S3 bucket named `tagging-log-<stack-suffix>` is created with `DeletionPolicy: Retain`. Deleting the stack will **not** delete this bucket — clean it up manually if you no longer need the logs.
- When `TrailS3Bucket` points to an existing bucket, no new bucket is created. Make sure the bucket policy grants `cloudtrail.amazonaws.com` permission to call `s3:GetBucketAcl` and `s3:PutObject` against the appropriate prefix.

### Modify tag
1. Open the Lambda console and select the Lambda function (default: `resource-tagging-automation-function`).
2. Go to the **Configuration** tab, select **Environment variables**, and click **Edit** to modify the `tags` value.
3. Update the value (JSON format) and click **Save**. Resources created after the update will receive the new tags.
