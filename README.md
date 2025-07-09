# 🧠 CloudOps Toolkit

A zero-cost internal cloud management dashboard built with Python, Streamlit, Terraform, and AWS Free Tier. Monitor your AWS resources, track costs, view logs, and deploy infrastructure—all from a single interface.

## 🌟 Features

- 🔍 **Resource Inventory**: View EC2 instances and S3 buckets
- 💰 **Cost Monitoring**: Track AWS spending with Cost Explorer integration
- 📈 **Log Monitoring**: View CloudWatch logs from Lambda functions
- 🚀 **Infrastructure Deployment**: Trigger Terraform deployments from the dashboard
- 🔒 **Secure**: Environment-based configuration with AWS credentials
- 🆓 **Zero Cost**: Designed to run entirely on AWS Free Tier

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python with boto3
- **Infrastructure**: Terraform
- **Cloud Provider**: AWS (Free Tier)
- **CI/CD**: GitHub Actions

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- AWS Account with appropriate permissions
- Terraform installed
- Git

### Installation

1. Clone the repository:
```bash
git clone https://github.com/lukeperry/CloudOps-toolkit
cd CloudOps-toolkit
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure AWS credentials:
```bash
cp .env.example .env
# Edit .env with your AWS credentials
```

5. Run the dashboard:
```bash
streamlit run app/dashboard.py
```

## 📁 Project Structure

```
CloudOps-toolkit/
├── app/                    # Application modules
│   ├── dashboard.py       # Main Streamlit dashboard
│   ├── aws_inventory.py   # EC2 and S3 inventory
│   ├── cost_explorer.py   # Cost monitoring
│   ├── cloudwatch_logs.py # Log viewing
│   ├── deploy_trigger.py  # Terraform deployment
│   └── utils.py          # Utility functions
├── terraform/             # Infrastructure as Code
│   ├── main.tf           # Main Terraform configuration
│   ├── variables.tf      # Variable definitions
│   └── outputs.tf        # Output definitions
├── .github/workflows/     # CI/CD pipelines
├── .streamlit/           # Streamlit configuration
├── requirements.txt      # Python dependencies
├── .env.example         # Environment template
└── run_dashboard.py     # Main entry point
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=ap-southeast-1
```

### AWS Permissions

This project requires specific AWS managed policies to function properly. Attach these policies to your IAM user:

#### Required AWS Managed Policies:
- **`AmazonEC2ReadOnlyAccess`** - For EC2 instance inventory
- **`CloudWatchLogsReadOnlyAccess`** - For viewing CloudWatch logs  
- **`AWSBillingReadOnlyAccess`** - For Cost Explorer functionality

#### For Terraform Infrastructure Deployment:
- **`IAMFullAccess`** - For creating Lambda execution roles
- **`AWSLambdaFullAccess`** - For creating/managing Lambda functions
- **`AmazonS3FullAccess`** - For S3 operations (includes inventory + demo buckets)
- **`CloudWatchFullAccess`** - For log groups, alarms, and log viewing

#### How to Apply:
1. Go to AWS Console → IAM → Users → your user
2. Click "Add permissions" → "Attach existing policies directly"
3. Search for and select each policy above
4. Click "Next" → "Add permissions"

**Note**: The "FullAccess" policies include read permissions, so you don't need separate read-only policies for those services.

## 📊 Usage

1. **Inventory**: View your EC2 instances and S3 buckets
2. **Cost**: Monitor AWS spending and get cost breakdowns
3. **Deploy**: Trigger Terraform deployments for infrastructure changes
4. **Monitoring**: View CloudWatch logs from your Lambda functions

## 🚀 Running the Dashboard

```bash
streamlit run app/dashboard.py
```

## 🎯 Portfolio Highlights

This project demonstrates:

- **Cloud Engineering**: AWS service integration with boto3
- **Infrastructure as Code**: Terraform for automated deployments
- **Full-Stack Development**: Python backend with Streamlit frontend
- **DevOps Practices**: CI/CD workflows and environment configuration
- **Security**: Proper credential handling and IAM policy management
- **Testing**: Unit tests with pytest and mocking
- **Documentation**: Comprehensive setup and usage guides

## 🛡️ Security Features

- Environment-based credential management
- IAM policy least-privilege principles
- Secure S3 bucket configurations
- CloudWatch monitoring and alerting

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details..
