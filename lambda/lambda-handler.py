# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import boto3
import os
import json

def aws_ec2(event):
    arnList = []
    _account = event['account']
    _region = event['region']
    ec2ArnTemplate = 'arn:aws:ec2:@region@:@account@:instance/@instanceId@'
    volumeArnTemplate = 'arn:aws:ec2:@region@:@account@:volume/@volumeId@'
    if event['detail']['eventName'] == 'RunInstances':
        print("tagging for new EC2...")
        _instanceId = event['detail']['responseElements']['instancesSet']['items'][0]['instanceId']
        arnList.append(ec2ArnTemplate.replace('@region@', _region).replace('@account@', _account).replace('@instanceId@', _instanceId))

        ec2_resource = boto3.resource('ec2')
        _instance = ec2_resource.Instance(_instanceId)
        for volume in _instance.volumes.all():
            arnList.append(volumeArnTemplate.replace('@region@', _region).replace('@account@', _account).replace('@volumeId@', volume.id))

    elif event['detail']['eventName'] == 'CreateVolume':
        print("tagging for new EBS...")
        _volumeId = event['detail']['responseElements']['volumeId']
        arnList.append(volumeArnTemplate.replace('@region@', _region).replace('@account@', _account).replace('@volumeId@', _volumeId))
        
    elif event['detail']['eventName'] == 'CreateInternetGateway':
        print("tagging for new IGW...")
        
    elif event['detail']['eventName'] == 'CreateNatGateway':
        print("tagging for new Nat Gateway...")
        
    elif event['detail']['eventName'] == 'AllocateAddress':
        print("tagging for new EIP...")
        arnList.append(event['detail']['responseElements']['allocationId'])
        
    elif event['detail']['eventName'] == 'CreateVpcEndpoint':
        print("tagging for new VPC Endpoint...")
        
    elif event['detail']['eventName'] == 'CreateTransitGateway':
        print("tagging for new Transit Gateway...")

    return arnList
    
def aws_elasticloadbalancing(event):
    arnList = []
    if event['detail']['eventName'] == 'CreateLoadBalancer':
        print("tagging for new LoadBalancer...")
        lbs = event['detail']['responseElements']
        for lb in lbs['loadBalancers']:
            arnList.append(lb['loadBalancerArn'])
        return arnList

def aws_rds(event):
    arnList = []
    if event['detail']['eventName'] == 'CreateDBInstance':
        print("tagging for new RDS...")
        #db_instance_id = event['detail']['requestParameters']['dBInstanceIdentifier']
        #waiter = boto3.client('rds').get_waiter('db_instance_available')
        #waiter.wait(
        #    DBInstanceIdentifier = db_instance_id
        #)
        arnList.append(event['detail']['responseElements']['dBInstanceArn'])
        return arnList

def aws_s3(event):
    arnList = []
    if event['detail']['eventName'] == 'CreateBucket':
        print("tagging for new S3...")
        _bkcuetName = event['detail']['requestParameters']['bucketName']
        arnList.append('arn:aws:s3:::' + _bkcuetName)
        return arnList
        
def aws_lambda(event):
    arnList = []
    _exist1 = event['detail']['responseElements']
    _exist2 = event['detail']['eventName'] == 'CreateFunction20150331'
    if  _exist1!= None and _exist2:
        function_name = event['detail']['responseElements']['functionName']
        print('Functin name is :', function_name)
        arnList.append(event['detail']['responseElements']['functionArn'])
        return arnList

def aws_dynamodb(event):
    arnList = []
    if event['detail']['eventName'] == 'CreateTable':
        table_name = event['detail']['responseElements']['tableDescription']['tableName']
        waiter = boto3.client('dynamodb').get_waiter('table_exists')
        waiter.wait(
            TableName=table_name,
            WaiterConfig={
                'Delay': 123,
                'MaxAttempts': 123
            }
        )
        arnList.append(event['detail']['responseElements']['tableDescription']['tableArn'])
        return arnList
        
def aws_kms(event):
    arnList = []
    if event['detail']['eventName'] == 'CreateKey':
        arnList.append(event['detail']['responseElements']['keyMetadata']['arn'])
        return arnList

def aws_sns(event):
    arnList = []
    _account = event['account']
    _region = event['region']
    snsArnTemplate = 'arn:aws:sns:@region@:@account@:@topicName@'
    if event['detail']['eventName'] == 'CreateTopic':
        print("tagging for new SNS...")
        _topicName = event['detail']['requestParameters']['name']
        arnList.append(snsArnTemplate.replace('@region@', _region).replace('@account@', _account).replace('@topicName@', _topicName))
        return arnList
        
def aws_sqs(event):
    arnList = []
    _account = event['account']
    _region = event['region']
    sqsArnTemplate = 'arn:aws:sqs:@region@:@account@:@queueName@'
    if event['detail']['eventName'] == 'CreateQueue':
        print("tagging for new SQS...")
        _queueName = event['detail']['requestParameters']['queueName']
        arnList.append(sqsArnTemplate.replace('@region@', _region).replace('@account@', _account).replace('@queueName@', _queueName))
        return arnList
        
def aws_elasticfilesystem(event):
    arnList = []
    _account = event['account']
    _region = event['region']
    efsArnTemplate = 'arn:aws:elasticfilesystem:@region@:@account@:file-system/@fileSystemId@'
    if event['detail']['eventName'] == 'CreateMountTarget':
        print("tagging for new efs...")
        _efsId = event['detail']['responseElements']['fileSystemId']
        arnList.append(efsArnTemplate.replace('@region@', _region).replace('@account@', _account).replace('@fileSystemId@', _efsId))
        return arnList
        
def aws_es(event):
    arnList = []
    if event['detail']['eventName'] == 'CreateDomain':
        print("tagging for new open search...")
        arnList.append(event['detail']['responseElements']['domainStatus']['aRN'])
        return arnList

def aws_elasticache(event):
    arnList = []
    _account = event['account']
    _region = event['region']
    ecArnTemplate = 'arn:aws:elasticache:@region@:@account@:cluster:@ecId@'

    if event['detail']['eventName'] == 'CreateReplicationGroup' or event['detail']['eventName'] == 'ModifyReplicationGroupShardConfiguration':
        print("tagging for new ElastiCache cluster...")
        _replicationGroupId = event['detail']['requestParameters']['replicationGroupId']
        waiter = boto3.client('elasticache').get_waiter('replication_group_available')
        waiter.wait(
            ReplicationGroupId = _replicationGroupId,
            WaiterConfig={
                'Delay': 123,
                'MaxAttempts': 123
            }
        )
        _clusters = event['detail']['responseElements']['memberClusters']
        for _ec in _clusters:
            arnList.append(ecArnTemplate.replace('@region@', _region).replace('@account@', _account).replace('@ecId@', _ec))

    elif event['detail']['eventName'] == 'CreateCacheCluster':
        print("tagging for new ElastiCache node...")
        _cacheClusterId = event['detail']['responseElements']['cacheClusterId']
        waiter = boto3.client('elasticache').get_waiter('cache_cluster_available')
        waiter.wait(
            CacheClusterId = _cacheClusterId,
            WaiterConfig={
                'Delay': 123,
                'MaxAttempts': 123
            }
        )
        arnList.append(event['detail']['responseElements']['aRN'])

    return arnList

def main(event, context):
    print("input event is: ")
    print(event)
    print("new source is " + event['source'])
    _method = event['source'].replace('.', "_")

    resARNs = globals()[_method](event)
    print("resource arn is: ")
    print(resARNs)

    _res_tags =  json.loads(os.environ['tags'])
    boto3.client('resourcegroupstaggingapi').tag_resources(
        ResourceARNList=resARNs,
        Tags=_res_tags
    )

    return {
        'statusCode': 200,
        'body': json.dumps('Finished map tagging with ' + event['source'])
    }
