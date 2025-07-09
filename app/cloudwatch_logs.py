# app/cloudwatch_logs.py

from utils import get_boto3_client
import logging
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_logs(log_group="/aws/lambda/your-function-name", limit=10):
    try:
        logs_client = get_boto3_client("logs")
        
        # First check if log group exists
        try:
            logs_client.describe_log_groups(logGroupNamePrefix=log_group)
        except Exception as e:
            if "ResourceNotFoundException" in str(e):
                return f"Log group '{log_group}' does not exist. The Lambda function may not have been invoked yet, or the log group name is incorrect."
            else:
                return f"Error accessing log group: {str(e)}"
        
        # Get log streams (increased limit and better sorting)
        response = logs_client.describe_log_streams(
            logGroupName=log_group,
            orderBy="LastEventTime",
            descending=True,
            limit=10  # Get more streams to check
        )
        
        # Check if there are any log streams
        if not response["logStreams"]:
            return f"No log streams found in '{log_group}'. The Lambda function may not have been executed yet."
        
        logger.info(f"Found {len(response['logStreams'])} log streams in {log_group}")
        
        # Try to find a stream with events (check all streams, not just ones with lastEventTime)
        for i, stream in enumerate(response["logStreams"]):
            stream_name = stream["logStreamName"]
            logger.info(f"Checking stream {i+1}: {stream_name}")
            
            try:
                events = logs_client.get_log_events(
                    logGroupName=log_group,
                    logStreamName=stream_name,
                    limit=limit,
                    startFromHead=False  # Get latest events
                )
                
                if events["events"]:
                    log_messages = []
                    for event in events["events"]:
                        timestamp = event["timestamp"]
                        message = event["message"].strip()
                        # Convert timestamp to readable format
                        import datetime
                        readable_time = datetime.datetime.fromtimestamp(timestamp/1000).strftime('%Y-%m-%d %H:%M:%S')
                        log_messages.append(f"[{readable_time}] {message}")
                    
                    logger.info(f"Found {len(events['events'])} log events in stream {stream_name}")
                    return "\n".join(log_messages)
                else:
                    logger.info(f"Stream {stream_name} has no events")
                    
            except Exception as stream_error:
                logger.warning(f"Error reading stream {stream_name}: {str(stream_error)}")
                continue
        
        # If we get here, no streams have events
        stream_info = []
        for stream in response["logStreams"]:
            last_event = stream.get("lastEventTime", "Never")
            if last_event != "Never":
                last_event = datetime.datetime.fromtimestamp(last_event/1000).strftime('%Y-%m-%d %H:%M:%S')
            stream_info.append(f"  • {stream['logStreamName']} (last event: {last_event})")
        
        return f"""Log group '{log_group}' exists with {len(response['logStreams'])} streams but contains no recent log events.

Streams found:
{chr(10).join(stream_info)}

💡 Tips:
- Lambda logs may take 10-30 seconds to appear
- Try waiting a moment and fetch logs again
- Make sure the Lambda function actually executed (check for success message)"""
        
    except Exception as e:
        logger.error(f"Error fetching logs from {log_group}: {str(e)}")
        return f"Error fetching logs: {str(e)}"

def list_available_log_groups():
    """
    List available CloudWatch log groups for the dashboard
    """
    try:
        logs_client = get_boto3_client("logs")
        response = logs_client.describe_log_groups(limit=50)
        
        log_groups = []
        for group in response["logGroups"]:
            log_groups.append({
                "name": group["logGroupName"],
                "creation_time": group["creationTime"],
                "size_bytes": group.get("storedBytes", 0)
            })
        
        return log_groups
    except Exception as e:
        logger.error(f"Error listing log groups: {str(e)}")
        return []

def trigger_lambda_function(function_name="cloudops-demo-function"):
    """
    Trigger a Lambda function to generate logs for testing
    """
    try:
        lambda_client = get_boto3_client("lambda")
        
        # Create a simple test event
        test_event = {
            "test": True,
            "message": "Test invocation from CloudOps Toolkit",
            "timestamp": datetime.now().isoformat()
        }
        
        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',
            Payload=json.dumps(test_event)
        )
        
        # Read the response
        response_payload = json.loads(response['Payload'].read())
        
        return {
            "success": True,
            "response": response_payload,
            "status_code": response.get("StatusCode", 200)
        }
        
    except Exception as e:
        logger.error(f"Error triggering Lambda function {function_name}: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

# This module provides functions to interact with AWS CloudWatch Logs and Lambda.
# It includes retrieving logs, listing log groups, and triggering Lambda functions for testing.