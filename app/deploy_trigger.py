# app/deploy_trigger.py

import subprocess
import os
import json
import logging
import re
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def strip_ansi_codes(text):
    """
    Strip ANSI color codes from text for clean display in web interfaces
    """
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def get_terraform_status():
    """
    Get current Terraform status and state information
    """
    try:
        # Check if terraform is initialized
        result = subprocess.run(
            ["terraform", "version"],
            cwd="terraform",
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            return {
                'terraform_available': True,
                'version': result.stdout.strip(),
                'initialized': os.path.exists("terraform/.terraform")
            }
        else:
            return {
                'terraform_available': False,
                'error': result.stderr
            }
            
    except subprocess.TimeoutExpired:
        return {
            'terraform_available': False,
            'error': "Terraform command timed out"
        }
    except Exception as e:
        return {
            'terraform_available': False,
            'error': str(e)
        }

def terraform_plan():
    """
    Run terraform plan and return the output
    """
    try:
        logger.info("Running terraform plan...")
        result = subprocess.run(
            ["terraform", "plan", "-out=tfplan"],
            cwd="terraform",
            capture_output=True,
            text=True,
            timeout=120
        )
        
        return {
            'success': result.returncode == 0,
            'output': strip_ansi_codes(result.stdout),
            'error': strip_ansi_codes(result.stderr) if result.returncode != 0 else None
        }
        
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': "Terraform plan timed out after 2 minutes"
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def terraform_apply():
    """
    Run terraform apply and return the output
    """
    try:
        logger.info("Running terraform apply...")
        result = subprocess.run(
            ["terraform", "apply", "-auto-approve", "tfplan"],
            cwd="terraform",
            capture_output=True,
            text=True,
            timeout=600  # 10 minutes
        )
        
        return {
            'success': result.returncode == 0,
            'output': strip_ansi_codes(result.stdout),
            'error': strip_ansi_codes(result.stderr) if result.returncode != 0 else None
        }
        
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': "Terraform apply timed out after 10 minutes"
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def terraform_destroy():
    """
    Run terraform destroy and return the output
    """
    try:
        logger.info("Running terraform destroy...")
        result = subprocess.run(
            ["terraform", "destroy", "-auto-approve"],
            cwd="terraform",
            capture_output=True,
            text=True,
            timeout=600  # 10 minutes
        )
        
        return {
            'success': result.returncode == 0,
            'output': strip_ansi_codes(result.stdout),
            'error': strip_ansi_codes(result.stderr) if result.returncode != 0 else None
        }
        
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': "Terraform destroy timed out after 10 minutes"
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def get_terraform_state():
    """
    Get current Terraform state information
    """
    try:
        result = subprocess.run(
            ["terraform", "show", "-json"],
            cwd="terraform",
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            try:
                state_data = json.loads(result.stdout)
                resources = state_data.get('values', {}).get('root_module', {}).get('resources', [])
                return {
                    'success': True,
                    'resources': len(resources),
                    'resource_list': [r.get('address', 'Unknown') for r in resources],
                    'state_data': state_data
                }
            except json.JSONDecodeError:
                return {
                    'success': False,
                    'error': "Failed to parse Terraform state JSON"
                }
        else:
            return {
                'success': False,
                'error': strip_ansi_codes(result.stderr) if result.stderr else "No state information available"
            }
            
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': "Terraform state check timed out"
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def trigger_terraform(action="plan"):
    """
    Trigger Terraform deployment with enhanced error handling
    """
    logger.info(f"Triggering Terraform action: {action}")
    
    if action == "plan":
        return terraform_plan()
    elif action == "apply":
        return terraform_apply()
    elif action == "destroy":
        return terraform_destroy()
    else:
        return {
            'success': False,
            'error': f"Unknown action: {action}. Supported actions: plan, apply, destroy"
        }

def get_terraform_outputs():
    """
    Get Terraform outputs after successful deployment
    """
    try:
        result = subprocess.run(
            ["terraform", "output", "-json"],
            cwd="terraform",
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            try:
                outputs = json.loads(result.stdout)
                return {
                    'success': True,
                    'outputs': outputs
                }
            except json.JSONDecodeError:
                return {
                    'success': False,
                    'error': "Failed to parse Terraform outputs JSON"
                }
        else:
            return {
                'success': False,
                'error': strip_ansi_codes(result.stderr) if result.stderr else "No outputs available"
            }
            
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': "Terraform outputs check timed out"
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }