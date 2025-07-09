import json
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    """
    Demo Lambda function for CloudOps Toolkit
    This function demonstrates basic logging and returns a simple response
    """
    
    # Log the incoming event
    logger.info(f"Received event: {json.dumps(event)}")
    
    # Demo functionality
    response_data = {
        "statusCode": 200,
        "message": "Hello from CloudOps Toolkit Demo Lambda!",
        "timestamp": context.aws_request_id,
        "function_name": context.function_name,
        "remaining_time": context.get_remaining_time_in_millis()
    }
    
    logger.info(f"Returning response: {json.dumps(response_data)}")
    
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(response_data)
    }
