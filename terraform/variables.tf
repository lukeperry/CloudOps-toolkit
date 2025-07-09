# CloudOps Toolkit - Terraform Variables

variable "aws_region" {
  description = "The AWS region to deploy resources in"
  type        = string
  default     = "ap-southeast-1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "lambda_function_name" {
  description = "Name of the Lambda function"
  type        = string
  default     = "cloudops-demo-function"
}

variable "s3_bucket_name" {
  description = "Base name for the S3 bucket (will have random suffix)"
  type        = string
  default     = "cloudops-demo-bucket"
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "CloudOps-Toolkit"
}

variable "owner" {
  description = "Owner of the resources"
  type        = string
  default     = "CloudOps-Team"
}

variable "cost_allocation_tags" {
  description = "Tags for cost allocation"
  type        = map(string)
  default = {
    Project     = "CloudOps-Toolkit"
    Environment = "dev"
    Owner       = "CloudOps-Team"
  }
}
