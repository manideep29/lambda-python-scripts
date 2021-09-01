import boto3
import csv

def lambda_handler(event, context):
    # EC2 Inventory details with Name Tag, Private IP Address, State, Instance Type, Region, Availability Zone, Instance ID, Owner ID, VPC ID, Subnet ID, Environment Tag
    ec2_client=boto3.client(service_name='ec2',region_name='us-east-1')
    s3_resource=boto3.resource(service_name='s3',region_name='us-east-1')
    aws_regions=ec2_client.describe_regions()['Regions']
    bucket=s3_resource.Bucket('boto3-testing-manideep')
    key_emptyfile='ec2-inventory/ec2-inventory.csv'
    key_newfile='ec2-inventory/ec2_inventory_latest.csv'
    
    local_file='/tmp/ec2_inventory.csv'
    bucket.download_file(key_emptyfile,local_file)
    sno=1
    csv_obj=open(local_file,"w",newline='')
    csv_writer=csv.writer(csv_obj)
    csv_writer.writerow(["S.No","Name","Private IP","Environment","State","Instance Type","Region","Availability Zone","Instance ID","Owner ID","VPC ID","Subnet ID"])
    for each_region in aws_regions:
        ec2_client=boto3.client(service_name='ec2',region_name=each_region['RegionName'])
        for each_reservation in ec2_client.describe_instances()['Reservations']:
            owner_id=each_reservation['OwnerId']
            for each_instance in each_reservation['Instances']:
                instance_privateip=each_instance['PrivateIpAddress']
                instance_state=each_instance['State']['Name']
                instance_type=each_instance['InstanceType']
                instance_region=each_region['RegionName']
                instance_availabilityzone=each_instance['Placement']['AvailabilityZone']
                instance_id=each_instance['InstanceId']
                vpc_id=each_instance['VpcId']
                subnet_id=each_instance['SubnetId']
                for each_tag in each_instance['Tags']:
                    name_tag="None"
                    environment_tag="None"
                    if each_tag['Key']=='Name':
                        name_tag=each_tag['Value']
                    elif each_tag['Key']=='Environment':
                        environment_tag=each_tag['Value']
                print(sno,name_tag,instance_privateip,environment_tag,instance_state,instance_type,instance_region,instance_availabilityzone,instance_id,owner_id,vpc_id,subnet_id)
                csv_writer.writerow([sno,name_tag,instance_privateip,environment_tag,instance_state,instance_type,instance_region,instance_availabilityzone,instance_id,owner_id,vpc_id,subnet_id])
                sno+=1
    csv_obj.close()
    bucket.upload_file(local_file, key_newfile)
    return {
        'statusCode': 200,
        'body': json.dumps('Script Executed successfully!')
    }
