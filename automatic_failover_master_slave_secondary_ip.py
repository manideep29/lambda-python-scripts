import json
import boto3
import sys
from pprint import pprint

def lambda_handler(event, context):
    # Two Servers "Master and Slave" in running state, get Master Slave information from Tags
    # Master has secondary IP address
    # If Master is stopped, re-assign secondary IP address to Slave
    ec2_client=boto3.client(service_name='ec2',region_name='us-east-1')
    ec2_resource=boto3.resource(service_name='ec2',region_name='us-east-1')
    print("Instance {} state has been changed to {}".format(event['detail']['instance-id'],event['detail']['state']))
    stopped_instance_id=event['detail']['instance-id']
    instance_ids=['i-046f91b20d06cbdf5','i-067d9c6f7ac1ccb7c']
    if stopped_instance_id not in instance_ids:
        print("Instance ID is not part of failover application")
        sys.exit()
    master_instance_id=''
    slave_instance_id=''
    master_instance_state=''
    slave_instance_state=''
    master_instance_eth=''
    slave_instance_eth=''
    
    for each_reservation in ec2_client.describe_instances(InstanceIds=instance_ids)['Reservations']:
        for each_instance in each_reservation['Instances']:
            for tags in each_instance['Tags']:
                if tags["Key"]=='ServerType' and tags["Value"]=='Master':
                    master_instance_id=each_instance['InstanceId']
                    master_instance_state=each_instance['State']['Name']
                    print("Master Instance ID is {} and status is {}".format(master_instance_id,master_instance_state))
                    for each_eth in each_instance['NetworkInterfaces']:
                        master_instance_eth=each_eth['NetworkInterfaceId']
                        print("Network interface ID is {} with Private IP addresses {}".format(master_instance_eth,each_eth['PrivateIpAddresses']))
                        for each_privateIp in each_eth['PrivateIpAddresses']:
                            if bool(each_privateIp['Primary'])==False:
                                secondary_ip_address=each_privateIp['PrivateIpAddress']
                                print("Secondary IP of Master server: {}".format(secondary_ip_address))
                elif tags["Key"]=='ServerType' and tags["Value"]=='Slave':
                    slave_instance_id=each_instance['InstanceId']
                    slave_instance_state=each_instance['State']['Name']
                    print("Slave Instance ID is {} and status is {}".format(slave_instance_id,slave_instance_state))
                    for each_eth in each_instance['NetworkInterfaces']:
                        slave_instance_eth=each_eth['NetworkInterfaceId']
                        print("Network interface ID is {} with Private IP addresses {}".format(slave_instance_eth,each_eth['PrivateIpAddresses']))
                        
    
    if master_instance_state=="stopped":
        print("Detaching the secondary IP from Master Server")
        ec2_client.unassign_private_ip_addresses(NetworkInterfaceId=master_instance_eth,PrivateIpAddresses=[secondary_ip_address])
        print("Modifying the ServerType Tag from Master to Slave")
        ec2_client.delete_tags(
            Resources=[master_instance_id],
            Tags=[
            {'Key': 'ServerType','Value': 'Master'}
            ]
        )
        ec2_client.create_tags(
            Resources=[master_instance_id],
            Tags=[
            {'Key': 'ServerType','Value': 'Slave'}
            ]
        )
        print("Attaching the secondary IP to Slave Server")
        ec2_client.assign_private_ip_addresses(AllowReassignment=True,NetworkInterfaceId=slave_instance_eth,PrivateIpAddresses=[secondary_ip_address])
        print("Modifying the ServerType Tag from Slave to Master")
        ec2_client.delete_tags(
            Resources=[slave_instance_id],
            Tags=[
            {'Key': 'ServerType','Value': 'Slave'}
            ]
        )
        ec2_client.create_tags(
            Resources=[slave_instance_id],
            Tags=[
            {'Key': 'ServerType','Value': 'Master'}
            ]
        )
        
    return {
        'statusCode': 200,
        'body': json.dumps('Script executed successfully!')
    }
