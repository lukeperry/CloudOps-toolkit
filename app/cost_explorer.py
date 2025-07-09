# app/cost_explorer.py

import logging
from utils import get_boto3_client
from datetime import datetime, timedelta
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_cost_summary():
    """
    Get AWS cost summary for the current month using Cost Explorer
    Returns a dictionary with cost information
    """
    try:
        ce = get_boto3_client("ce")
        end = datetime.utcnow().date()
        start = end.replace(day=1)

        response = ce.get_cost_and_usage(
            TimePeriod={
                "Start": start.strftime('%Y-%m-%d'),
                "End": end.strftime('%Y-%m-%d')
            },
            Granularity="MONTHLY",
            Metrics=["UnblendedCost"]
        )

        if response["ResultsByTime"]:
            amount = response["ResultsByTime"][0]["Total"]["UnblendedCost"]["Amount"]
            logger.info(f"Successfully retrieved cost data: ${amount}")
            return {
                "Month": start.strftime("%B %Y"),
                "Cost (USD)": round(float(amount), 4),
                "Currency": "USD",
                "Period": f"{start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')}"
            }
        else:
            return {"Error": "No cost data available for the current month"}
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error retrieving cost data: {error_msg}")
        
        # Check for specific Cost Explorer errors
        if "AccessDeniedException" in error_msg or "not enabled for cost explorer" in error_msg.lower():
            return {
                "Error": "Cost Explorer not enabled",
                "Message": "Please enable Cost Explorer in AWS Billing Console. It may take up to 24 hours to activate.",
                "Instructions": [
                    "1. Go to AWS Billing and Cost Management",
                    "2. Click on 'Cost Explorer' in the left sidebar",
                    "3. Click 'Enable Cost Explorer'",
                    "4. Wait 24 hours for activation"
                ]
            }
        else:
            return {"Error": f"Failed to retrieve cost data: {error_msg}"}

def get_cost_by_service():
    """
    Get AWS cost breakdown by service for the current month
    Returns a list of dictionaries with service-wise costs
    """
    try:
        ce = get_boto3_client("ce")
        end = datetime.utcnow().date()
        start = end.replace(day=1)

        response = ce.get_cost_and_usage(
            TimePeriod={
                "Start": start.strftime('%Y-%m-%d'),
                "End": end.strftime('%Y-%m-%d')
            },
            Granularity="MONTHLY",
            Metrics=["UnblendedCost"],
            GroupBy=[
                {
                    'Type': 'DIMENSION',
                    'Key': 'SERVICE'
                }
            ]
        )

        services = []
        if response["ResultsByTime"]:
            for group in response["ResultsByTime"][0]["Groups"]:
                service_name = group["Keys"][0]
                cost = float(group["Metrics"]["UnblendedCost"]["Amount"])
                if cost > 0:  # Only include services with actual costs
                    services.append({
                        "Service": service_name,
                        "Cost (USD)": round(cost, 4)
                    })
        
        # Sort by cost (highest first)
        services.sort(key=lambda x: x["Cost (USD)"], reverse=True)
        logger.info(f"Successfully retrieved cost data for {len(services)} services")
        return services
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error retrieving cost by service: {error_msg}")
        
        if "AccessDeniedException" in error_msg or "not enabled for cost explorer" in error_msg.lower():
            return [{
                "Error": "Cost Explorer not enabled",
                "Message": "Please enable Cost Explorer in AWS Billing Console and wait 24 hours for activation."
            }]
        else:
            return [{"Error": f"Failed to retrieve cost by service: {error_msg}"}]

def get_daily_costs(days=30):
    """
    Get daily cost data for the last N days
    Returns a list of dictionaries with daily costs
    """
    try:
        ce = get_boto3_client("ce")
        end = datetime.utcnow().date()
        start = end - timedelta(days=days)

        response = ce.get_cost_and_usage(
            TimePeriod={
                "Start": start.strftime('%Y-%m-%d'),
                "End": end.strftime('%Y-%m-%d')
            },
            Granularity="DAILY",
            Metrics=["UnblendedCost"]
        )

        daily_costs = []
        for result in response["ResultsByTime"]:
            cost = float(result["Total"]["UnblendedCost"]["Amount"])
            daily_costs.append({
                "Date": result["TimePeriod"]["Start"],
                "Cost (USD)": round(cost, 4)
            })

        logger.info(f"Successfully retrieved {len(daily_costs)} days of cost data")
        return daily_costs
    except Exception as e:
        logger.error(f"Error retrieving daily costs: {str(e)}")
        return [{"Error": f"Failed to retrieve daily costs: {str(e)}"}]

def get_cost_forecast():
    """
    Get cost forecast for the next 30 days
    Returns a dictionary with forecast information
    """
    try:
        ce = get_boto3_client("ce")
        start = datetime.utcnow().date()
        end = start + timedelta(days=30)

        response = ce.get_cost_forecast(
            TimePeriod={
                "Start": start.strftime('%Y-%m-%d'),
                "End": end.strftime('%Y-%m-%d')
            },
            Metric="UNBLENDED_COST",
            Granularity="MONTHLY"
        )

        forecast_amount = float(response["Total"]["Amount"])
        logger.info(f"Successfully retrieved cost forecast: ${forecast_amount}")
        return {
            "Forecast Period": f"{start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')}",
            "Forecasted Cost (USD)": round(forecast_amount, 4),
            "Currency": "USD"
        }
    except Exception as e:
        logger.error(f"Error retrieving cost forecast: {str(e)}")
        return {"Error": f"Failed to retrieve cost forecast: {str(e)}"}
