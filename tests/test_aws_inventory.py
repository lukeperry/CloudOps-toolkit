import sys
import os
import unittest.mock as mock

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.aws_inventory import list_ec2_instances, list_s3_buckets, get_resource_summary


class TestAWSInventory:
    """Test cases for AWS inventory functions"""
    
    @mock.patch('app.aws_inventory.get_boto3_client')
    def test_list_ec2_instances_success(self, mock_client):
        """Test successful EC2 instance listing"""
        # Mock EC2 client response
        mock_ec2 = mock.MagicMock()
        mock_client.return_value = mock_ec2
        
        from datetime import datetime
        mock_ec2.describe_instances.return_value = {
            'Reservations': [
                {
                    'Instances': [
                        {
                            'InstanceId': 'i-123456789',
                            'InstanceType': 't2.micro',
                            'State': {'Name': 'running'},
                            'Placement': {'AvailabilityZone': 'us-east-1a'},
                            'LaunchTime': datetime(2023, 1, 1, 12, 0, 0),
                            'PrivateIpAddress': '10.0.0.1',
                            'PublicIpAddress': '1.2.3.4',
                            'Tags': [{'Key': 'Name', 'Value': 'test-instance'}]
                        }
                    ]
                }
            ]
        }
        
        result = list_ec2_instances()
        
        assert len(result) == 1
        assert result[0]['Instance ID'] == 'i-123456789'
        assert result[0]['Type'] == 't2.micro'
        assert result[0]['State'] == 'running'
        assert result[0]['Name'] == 'test-instance'
        assert result[0]['Private IP'] == '10.0.0.1'
        assert result[0]['Public IP'] == '1.2.3.4'
    
    @mock.patch('app.aws_inventory.get_boto3_client')
    def test_list_ec2_instances_error(self, mock_client):
        """Test EC2 instance listing with error"""
        mock_client.side_effect = Exception("AWS connection failed")
        
        result = list_ec2_instances()
        
        assert len(result) == 1
        assert "Error" in result[0]
        assert "AWS connection failed" in result[0]["Error"]
    
    @mock.patch('app.aws_inventory.get_boto3_client')
    def test_list_s3_buckets_success(self, mock_client):
        """Test successful S3 bucket listing"""
        # Mock S3 client response
        mock_s3 = mock.MagicMock()
        mock_client.return_value = mock_s3
        
        from datetime import datetime
        mock_s3.list_buckets.return_value = {
            'Buckets': [
                {
                    'Name': 'test-bucket',
                    'CreationDate': datetime(2023, 1, 1, 12, 0, 0)
                }
            ]
        }
        
        mock_s3.get_bucket_location.return_value = {'LocationConstraint': 'us-west-2'}
        
        result = list_s3_buckets()
        
        assert len(result) == 1
        assert result[0]['Bucket Name'] == 'test-bucket'
        assert result[0]['Created On'] == '2023-01-01'
        assert result[0]['Region'] == 'us-west-2'
    
    @mock.patch('app.aws_inventory.get_boto3_client')
    def test_list_s3_buckets_error(self, mock_client):
        """Test S3 bucket listing with error"""
        mock_client.side_effect = Exception("S3 access denied")
        
        result = list_s3_buckets()
        
        assert len(result) == 1
        assert "Error" in result[0]
        assert "S3 access denied" in result[0]["Error"]
    
    @mock.patch('app.aws_inventory.get_boto3_client')
    def test_list_s3_buckets_none_region(self, mock_client):
        """Test S3 bucket listing with None region (us-east-1)"""
        # Mock S3 client response
        mock_s3 = mock.MagicMock()
        mock_client.return_value = mock_s3
        
        from datetime import datetime
        mock_s3.list_buckets.return_value = {
            'Buckets': [
                {
                    'Name': 'test-bucket-us-east-1',
                    'CreationDate': datetime(2023, 1, 1, 12, 0, 0)
                }
            ]
        }
        
        # When LocationConstraint is None, it means us-east-1
        mock_s3.get_bucket_location.return_value = {'LocationConstraint': None}
        
        result = list_s3_buckets()
        
        assert len(result) == 1
        assert result[0]['Bucket Name'] == 'test-bucket-us-east-1'
        assert result[0]['Region'] == 'us-east-1'
    
    @mock.patch('app.aws_inventory.list_ec2_instances')
    @mock.patch('app.aws_inventory.list_s3_buckets')
    def test_get_resource_summary_success(self, mock_s3, mock_ec2):
        """Test successful resource summary"""
        mock_ec2.return_value = [
            {'State': 'running'},
            {'State': 'stopped'},
            {'State': 'running'}
        ]
        
        mock_s3.return_value = [
            {'Bucket Name': 'bucket1'},
            {'Bucket Name': 'bucket2'}
        ]
        
        result = get_resource_summary()
        
        assert result['Total EC2 Instances'] == 3
        assert result['Running Instances'] == 2
        assert result['Stopped Instances'] == 1
        assert result['Total S3 Buckets'] == 2
        assert 'Last Updated' in result
