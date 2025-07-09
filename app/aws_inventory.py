# app/aws_inventory.py

import logging
from datetime import datetime
from utils import get_boto3_client
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def list_ec2_instances():
    """
    Get a list of running EC2 instances using boto3
    Returns a list of dictionaries containing instance details
    """
    try:
        ec2 = get_boto3_client("ec2")
        response = ec2.describe_instances()
        
        instances = []
        for reservation in response["Reservations"]:
            for instance in reservation["Instances"]:
                # Get instance name from tags
                instance_name = "N/A"
                if 'Tags' in instance:
                    for tag in instance['Tags']:
                        if tag['Key'] == 'Name':
                            instance_name = tag['Value']
                            break
                
                instances.append({
                    "Instance ID": instance["InstanceId"],
                    "Name": instance_name,
                    "Type": instance["InstanceType"],
                    "State": instance["State"]["Name"],
                    "AZ": instance["Placement"]["AvailabilityZone"],
                    "Private IP": instance.get("PrivateIpAddress", "N/A"),
                    "Public IP": instance.get("PublicIpAddress", "N/A"),
                    "Launch Time": instance["LaunchTime"].strftime('%Y-%m-%d %H:%M:%S') if "LaunchTime" in instance else "N/A"
                })
        
        logger.info(f"Successfully retrieved {len(instances)} EC2 instances")
        return instances
    except Exception as e:
        logger.error(f"Error retrieving EC2 instances: {str(e)}")
        return [{"Error": f"Failed to retrieve EC2 instances: {str(e)}"}]

def list_s3_buckets():
    """
    Get a list of S3 buckets using boto3
    Returns a list of dictionaries containing bucket details
    """
    try:
        s3 = get_boto3_client("s3")
        response = s3.list_buckets()
        
        buckets = []
        for bucket in response["Buckets"]:
            try:
                # Get bucket region
                bucket_region = s3.get_bucket_location(Bucket=bucket["Name"])['LocationConstraint']
                if bucket_region is None:
                    bucket_region = "us-east-1"
                
                # Get bucket size (this is a simplified approach)
                bucket_info = {
                    "Bucket Name": bucket["Name"],
                    "Created On": bucket["CreationDate"].strftime('%Y-%m-%d'),
                    "Region": bucket_region
                }
                buckets.append(bucket_info)
            except Exception as bucket_error:
                logger.warning(f"Error getting details for bucket {bucket['Name']}: {str(bucket_error)}")
                buckets.append({
                    "Bucket Name": bucket["Name"],
                    "Created On": bucket["CreationDate"].strftime('%Y-%m-%d'),
                    "Region": "Unknown"
                })
        
        logger.info(f"Successfully retrieved {len(buckets)} S3 buckets")
        return buckets
    except Exception as e:
        logger.error(f"Error retrieving S3 buckets: {str(e)}")
        return [{"Error": f"Failed to retrieve S3 buckets: {str(e)}"}]

def get_resource_summary():
    """
    Get a summary of AWS resources
    Returns a dictionary with resource counts
    """
    try:
        ec2_instances = list_ec2_instances()
        s3_buckets = list_s3_buckets()
        
        # Filter out error entries
        ec2_count = len([i for i in ec2_instances if "Error" not in i])
        s3_count = len([b for b in s3_buckets if "Error" not in b])
        
        running_instances = len([i for i in ec2_instances if i.get("State") == "running"])
        stopped_instances = len([i for i in ec2_instances if i.get("State") == "stopped"])
        
        return {
            "Total EC2 Instances": ec2_count,
            "Running Instances": running_instances,
            "Stopped Instances": stopped_instances,
            "Total S3 Buckets": s3_count,
            "Last Updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        logger.error(f"Error getting resource summary: {str(e)}")
        return {"Error": f"Failed to get resource summary: {str(e)}"}

def get_ec2_instances_by_state():
    """
    Get EC2 instances grouped by state for visualization
    Returns a dictionary with state as key and count as value
    """
    try:
        instances = list_ec2_instances()
        if not instances or "Error" in instances[0]:
            return {}
        
        state_counts = {}
        for instance in instances:
            state = instance.get("State", "unknown")
            state_counts[state] = state_counts.get(state, 0) + 1
        
        return state_counts
    except Exception as e:
        logger.error(f"Error getting EC2 instances by state: {str(e)}")
        return {}  
