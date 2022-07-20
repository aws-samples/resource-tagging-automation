# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from aws_cdk import (
    CfnParameter,
    Duration,
    Stack,
    aws_iam as _iam,
    aws_events as _events,
    aws_events_targets as _targets,
    aws_lambda as _lambda
)
from constructs import Construct

class ResourceTaggingStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # set parameters
        tags = CfnParameter(self, "tags", type="String", description="tag name and value with json format.")

        # create role for lambda function
        lambda_role = _iam.Role(self, "lambda_role",
            role_name = "resource-tagging-role",
            assumed_by=_iam.ServicePrincipal("lambda.amazonaws.com"))

        lambda_role.add_managed_policy(_iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"))
        lambda_role.add_to_policy(_iam.PolicyStatement(
            effect=_iam.Effect.ALLOW,
            resources=["*"],
            actions=["dynamodb:TagResource", "dynamodb:DescribeTable", "lambda:TagResource", "lambda:ListTags", "s3:GetBucketTagging", "s3:PutBucketTagging", 
            "ec2:CreateTags", "ec2:DescribeNatGateways", "ec2:DescribeInternetGateways", "ec2:DescribeVolumes", "rds:AddTagsToResource", "rds:DescribeDBInstances",
            "sns:TagResource", "sqs:ListQueueTags", "sqs:TagQueue", "es:AddTags", "kms:ListResourceTags", "kms:TagResource", "elasticfilesystem:TagResource", 
            "elasticfilesystem:CreateTags", "elasticfilesystem:DescribeTags", "elasticloadbalancing:AddTags", "logs:CreateLogGroup", "logs:CreateLogStream", 
            "logs:PutLogEvents", "tag:getResources", "tag:getTagKeys", "tag:getTagValues", "tag:TagResources", "tag:UntagResources", "cloudformation:DescribeStacks", 
            "cloudformation:ListStackResources", "elasticache:DescribeReplicationGroups", "elasticache:DescribeCacheClusters", "elasticache:AddTagsToResource","resource-groups:*"]
        ))

        # create lambda function
        tagging_function = _lambda.Function(self, "resource_tagging_automation_function",
                                    runtime=_lambda.Runtime.PYTHON_3_8,
                                    memory_size=128,
                                    timeout=Duration.seconds(600),
                                    handler="lambda-handler.main",
                                    code=_lambda.Code.from_asset("./lambda"),
                                    function_name="resource-tagging-automation-function",
                                    role=lambda_role,
                                    environment={
                                        "tags": tags.value_as_string
                                    }
                        )

        _eventRule = _events.Rule(self, "resource-tagging-automation-rule",
                        event_pattern=_events.EventPattern(
                            source=["aws.ec2", "aws.elasticloadbalancing", "aws.rds", "aws.lambda", "aws.s3", "aws.dynamodb", "aws.elasticfilesystem", "aws.es", "aws.sqs", "aws.sns", "aws.kms", "aws.elasticache"],
                            detail={
                                "eventSource": ["ec2.amazonaws.com", "elasticloadbalancing.amazonaws.com", "s3.amazonaws.com", "rds.amazonaws.com", "lambda.amazonaws.com", "dynamodb.amazonaws.com", "elasticfilesystem.amazonaws.com", "es.amazonaws.com", "sqs.amazonaws.com", "sns.amazonaws.com", "kms.amazonaws.com", "elasticache.amazonaws.com"],
                                "eventName": ["RunInstances", "CreateFunction20150331", "CreateBucket", "CreateDBInstance", "CreateTable", "CreateVolume", "CreateLoadBalancer", "CreateMountTarget", "CreateDomain", "CreateQueue", "CreateTopic", "CreateKey", "CreateReplicationGroup", "CreateCacheCluster", "ModifyReplicationGroupShardConfiguration"]
                            }
                        )
                    )

        _eventRule.add_target(_targets.LambdaFunction(tagging_function,
            retry_attempts=2
        )
)