import json
import boto3
from pprint import pprint;

def lambda_handler(event, context):
    #ec2_client=boto3.client(service_name="ec2",region_name="us-east-1")
    sns_client=boto3.client(service_name="sns",region_name="us-east-1")
    pprint(event)
    instance_id=event['detail']['instance-id']
    #print("Instance with ID {} has been stopped".format(instance_id))
    sns_client.publish(TopicArn="arn:aws:sns:us-east-1:766797037448:lambda-notifications-personal",Message="Instance with ID {} has been stopped".format(instance_id))
    return {
        'statusCode': 200,
        'body': json.dumps('Script executed successfully!')
    }
