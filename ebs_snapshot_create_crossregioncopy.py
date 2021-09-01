import json
import boto3
from pprint import pprint

def lambda_handler(event, context):
    source_region="us-east-1"
    destination_region="us-west-2"
    ec2_client=boto3.client(service_name="ec2",region_name="us-east-1")
    sns_client=boto3.client(service_name="sns",region_name="us-east-1")
    #f1={"Name":"status","Values":['in-use']}
    f2={"Name":"tag:Environment","Values":['Prod']}
    volume_ids=[]
    snapshot_ids=[]
    copy_snapshot_ids=[]
    ec2_client=boto3.client(service_name="ec2",region_name=source_region)
    paginator_describevolumes=ec2_client.get_paginator('describe_volumes')
    
    for each_page in paginator_describevolumes.paginate(Filters=[f2]):
        for each in each_page['Volumes']:
            volume_ids.append(each['VolumeId'])
    print("Volumes which are tagged with Production Environment:", volume_ids)
    
    for each_volume in volume_ids:
        snapshot_info=ec2_client.create_snapshot(VolumeId=each_volume)
        snapshot_ids.append(snapshot_info['SnapshotId'])
        print("Snapshot for Volume ID {}is triggered and Snapshot ID is: {}".format(snapshot_info['VolumeId'],snapshot_info['SnapshotId']))
        
    waiter_snapshotcreated=ec2_client.get_waiter('snapshot_completed')
    waiter_snapshotcreated.wait(SnapshotIds=snapshot_ids)
    print("Snapshots completed successfully: {}".format(snapshot_ids))
    ec2_client=boto3.client(service_name="ec2",region_name=destination_region)
    for each_snapshot in snapshot_ids:
        copy_snapshot_info=ec2_client.copy_snapshot(
            SourceRegion=source_region,
            SourceSnapshotId=each_snapshot
            #DestinationRegion="ec2.{}.amazonaws.com".format(destination_region)
            )
        copy_snapshot_ids.append(copy_snapshot_info['SnapshotId'])
    
    #print(waiter_snapshotcreated)
    print("Prod snapshots have been copied to {} and Snapshot IDs are {}".format(destination_region,copy_snapshot_ids))
    #sns_client.publish(TopicArn="arn:aws:sns:us-east-1:766797037448:lambda-notifications-personal",Message="Daily snapshots for Prod EBS volumes {} completed successfully with snapshot ids {} respectively".format(volume_ids,snapshot_ids),Subject="Daily Snapshots status")
