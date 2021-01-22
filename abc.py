
import boto3
import pprint
import json
import sys,argparse
from test_tags import load_yaml,get_all_res, dump_all_tags,each_validation, tag_validation 
#import pprint
#pp = pprint.PrettyPrinter(indent=4)
from yaml import safe_load, dump


pp = pprint.PrettyPrinter(indent=4)
client_ec2 = boto3.client('ec2')
client_s3 = boto3.client('s3')
client_rds = boto3.client('rds')
client_lambda = boto3.client('lambda')
client_cloudwatch = boto3.client('cloudwatch')
client_ecs = boto3.client('ecs')
ecs_arns,cloudwatch_arns,s3_buckets, rds_arns = [], [], [], []
untagged = []
def dump_untagged():
    with open('untagged.log','w') as out_file:
        for i in untagged:
            out_file.write(str(i))
            out_file.write('\n') 

def get_ec2_details():
    response = client_ec2.describe_instances()
    #pp.pprint(response)
    #pp.pprint(response['Reservations'])#'ResponseMetadata'
    for each_instance in response['Reservations']:
        for i in each_instance['Instances']:
            try:

                 
                if  i.get('Tags',0)==0:
                    print('Tags are not found for ec2 instance : {}'.format(i['InstanceId']))
                    str1 =f'tags are not found for ec2 instance whose id is : {i["InstanceId"]}' 
                    if str1 not in untagged:
                        untagged.append(str1)
                #pp.pprint(i.get('Tags'))
                #print(i.keys())
            except Exception as e:
                print(e)
                continue
    untagged.append('##########end of ec2 logs##########')
def get_s3_tagging():
    response = client_s3.list_buckets()
    #pp.pprint(response)
    for each in response['Buckets']:
        #print(each['Name'])
        s3_buckets.append(each['Name'])
    for each in s3_buckets:
        try:
            response = client_s3.get_bucket_tagging(Bucket=each)
            #pp.pprint(response)
            #print(response.keys())
        except Exception as e:
            #print('error occured while search tags for {}'.format(each))
            #print(e)
            str1 = f'tags are not found for s3 bucket whose name is {each}'
            print(str1)
            if str1 not in untagged:
                untagged.append(str1)
            continue
    untagged.append('##########end of s3 logs##########')

def get_rds_tagging():
    response = client_rds.describe_db_instances()
    #pp.pprint(response)
    for each in response.get('DBInstances'):
        print(each.get('DBInstanceArn'))
        if each.get('DBInstanceArn') not in rds_arns:
            rds_arns.append(each.get('DBInstanceArn'))
    for every in rds_arns:
        response_rds_tags = client_rds.list_tags_for_resource(ResourceName=every)
        pp.pprint(response_rds_tags)
        print(response_rds_tags.get('TagList'),'debug1')
        try:
            if  response_rds_tags.get('TagList',0)==[]:
                print('Tags are not found for RDS instance : {}'.format(every))
                str1 =f'tags are not found for RDS instance whose ARN is : {every}' 
                if str1 not in untagged:
                    untagged.append(str1)
            #pp.pprint(i.get('Tags'))
            #print(i.keys())
        except Exception as e:
            print(e)
            continue
    untagged.append('##########end of RDS untagged logs##########')


def get_lambdas_untagged():
    response_list_func = client_lambda.list_functions()
    #pp.pprint(response_list_func)
    print(response_list_func.keys())
    for each_arn in response_list_func['Functions']:
        print(each_arn['FunctionArn'])
        response = client_lambda.list_tags(Resource = each_arn['FunctionArn']) 
        #pp.pprint(response['Tags']) 
        try:

            if len(response['Tags'])==0:
                str1 = f'Tags are not found for lambda and it"s Arn is : {each_arn["FunctionArn"]}'
                print(str1)
                if str1 not in untagged:
                    untagged.append(str1)
                #pp.pprint(i.get('Tags'))
                #print(i.keys())
        except Exception as e:
            print(e)
            continue
    untagged.append('##########end of Lambda untagged logs##########')

def get_ebs_untagged():
    response = client_ec2.describe_volumes()
    pp.pprint(response['Volumes'])
    for each in response['Volumes']:
        try:
            if 'Tags' not in each.keys():
                str1 = f'Tags are not found for ebs and it"s id is : {each["VolumeId"]}'
                print(str1)
                if str1 not in untagged:
                    untagged.append(str1)
                #pp.pprint(i.get('Tags'))
                #print(i.keys())
        except Exception as e:
            print(e)
            continue
    untagged.append('##########end of EBS untagged logs##########')

def get_cloudwatch_untagged():
    response_dashboard = client_cloudwatch.list_dashboards()
    response_alarm = client_cloudwatch.describe_alarms()
    #pp.pprint(response_alarm['MetricAlarms'])
    for each in response_dashboard['DashboardEntries']:
        cloudwatch_arns.append(each['DashboardArn'])
    for every in response_alarm['MetricAlarms']:
        #print(every['AlarmArn'])
        cloudwatch_arns.append(every['AlarmArn'])
    for i in cloudwatch_arns:
        response_untagged = client_cloudwatch.list_tags_for_resource(ResourceARN=i)
        if len(response_untagged['Tags']) ==0:
            str1 = f'Tags are not found for a cloudwatch resource and it"s Arn is {i}'
            print(str1)
            if str1 not in untagged:
                untagged.append(str1)
    untagged.append('##########end of cloudwatch untagged logs##########')

def get_ecs_untagged():
    #print(response_tasks)
    #print(response_task_def)
    response_clusters = client_ecs.describe_clusters()
    #for each in response_clusters['clusters']:
    try:
        response_tasks = client_ecs.list_tasks()
        response_services = client.list_services()
        response_task_def = client_ecs.list_task_definitions()
        response_container_instances = client_ecs.list_container_instances()
        if response_tasks['taskArns']:
           ecs_arns.extend(response_tasks['taskArns'])
        if response_services['serviceArns']:
           ecs_arns.extend(response_services['serviceArns'])
        if response_services['taskDefinitionArns']:
           ecs_arns.extend(response_services['taskDefinitionArns'])
        if response_services['containerInstanceArns']:
           ecs_arns.extend(response_services['containerInstanceArns'])
        for i in ecs_arns:
            response_ecs_arns = client.list_tags_for_resource(resourceArn=i)
            if len(response_ecs_arns['tags'])==0:
                str1 = f'Tags are not found for ecs resources whose arn is :{i}'
                if str1 not in untagged:
                    untagged.append(str1)
    except Exception as e:
        print(e)
    for each in response_clusters['clusters']:
        if len(each['tags'])==0:
            str1 = f'Tags are not found for a ecs cluster. It"s arn is :{each["clusterArn"]}'
            if str1 not in untagged:
                untagged.append(str1)

    untagged.append('##########end of ecs untagged logs##########')


load_yaml(filename='data.yaml')
get_all_res()
dump_all_tags()
each_validation()

#get_ec2_details()
#get_s3_tagging()
#get_rds_tagging()
#get_ebs_untagged()
#get_lambdas_untagged()
#get_cloudwatch_untagged()
#get_ecs_untagged()
#dump_untagged()
