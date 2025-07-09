# app/dashboard.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from aws_inventory import list_ec2_instances, list_s3_buckets, get_resource_summary, get_ec2_instances_by_state
from cost_explorer import get_cost_summary, get_cost_by_service, get_daily_costs, get_cost_forecast
from deploy_trigger import trigger_terraform, get_terraform_status, get_terraform_state, get_terraform_outputs
from cloudwatch_logs import get_logs, list_available_log_groups, trigger_lambda_function

# Configure Streamlit page
st.set_page_config(
    page_title="CloudOps Toolkit", 
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .sidebar .sidebar-content {
        background-color: #f0f2f6;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🧠 CloudOps Toolkit Dashboard</h1>', unsafe_allow_html=True)

# Sidebar
st.sidebar.title("🧠 Navigation")
st.sidebar.markdown("---")

# Add refresh button
if st.sidebar.button("🔄 Refresh Data"):
    st.rerun()

# Add current time
st.sidebar.markdown(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Navigation menu
menu = st.sidebar.radio(
    "Select a section:",
    ["📊 Overview", "🔍 Inventory", "💰 Cost Analysis", "🚀 Deploy", "📈 Monitoring"],
    key="navigation"
)

# Overview Page
if menu == "📊 Overview":
    st.header("� Resource Overview")
    
    # Get resource summary
    summary = get_resource_summary()
    
    if "Error" not in summary:
        # Create metrics columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Total EC2 Instances",
                value=summary.get("Total EC2 Instances", 0),
                delta=None
            )
        
        with col2:
            st.metric(
                label="Running Instances",
                value=summary.get("Running Instances", 0),
                delta=None
            )
        
        with col3:
            st.metric(
                label="Stopped Instances",
                value=summary.get("Stopped Instances", 0),
                delta=None
            )
        
        with col4:
            st.metric(
                label="S3 Buckets",
                value=summary.get("Total S3 Buckets", 0),
                delta=None
            )
        
        # EC2 Instances by State Chart
        st.subheader("EC2 Instances by State")
        ec2_states = get_ec2_instances_by_state()
        
        if ec2_states:
            fig = px.pie(
                values=list(ec2_states.values()),
                names=list(ec2_states.keys()),
                title="EC2 Instance States"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No EC2 instances found or data unavailable")
    else:
        st.error(f"Error loading overview: {summary.get('Error', 'Unknown error')}")

# Inventory Page
elif menu == "🔍 Inventory":
    st.header("🔍 AWS Resource Inventory")
    
    # Create tabs for different resources
    tab1, tab2 = st.tabs(["🖥️ EC2 Instances", "🗄️ S3 Buckets"])
    
    with tab1:
        st.subheader("EC2 Instances")
        
        with st.spinner("Loading EC2 instances..."):
            instances = list_ec2_instances()
        
        if instances and "Error" not in instances[0]:
            # Convert to DataFrame for better display
            df = pd.DataFrame(instances)
            
            # Add filters
            col1, col2 = st.columns(2)
            with col1:
                states = df['State'].unique()
                selected_states = st.multiselect("Filter by State:", states, default=states)
            
            with col2:
                instance_types = df['Type'].unique()
                selected_types = st.multiselect("Filter by Type:", instance_types, default=instance_types)
            
            # Apply filters
            filtered_df = df[
                (df['State'].isin(selected_states)) & 
                (df['Type'].isin(selected_types))
            ]
            
            st.dataframe(filtered_df, use_container_width=True)
            
            # Download button
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"ec2_instances_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.warning("No EC2 instances found or failed to connect.")
            if instances and "Error" in instances[0]:
                st.error(instances[0]["Error"])
    
    with tab2:
        st.subheader("S3 Buckets")
        
        with st.spinner("Loading S3 buckets..."):
            buckets = list_s3_buckets()
        
        if buckets and "Error" not in buckets[0]:
            df = pd.DataFrame(buckets)
            st.dataframe(df, use_container_width=True)
            
            # Download button
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"s3_buckets_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.warning("No S3 buckets found or failed to connect.")
            if buckets and "Error" in buckets[0]:
                st.error(buckets[0]["Error"])

# Cost Analysis Page
elif menu == "💰 Cost Analysis":
    st.header("💰 AWS Cost Analysis")
    
    # Create tabs for different cost views
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Summary", "🔍 By Service", "📈 Daily Trend", "🔮 Forecast"])
    
    with tab1:
        st.subheader("Monthly Cost Summary")
        
        with st.spinner("Loading cost data..."):
            cost_data = get_cost_summary()
        
        if "Error" not in cost_data:
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    label=f"Cost for {cost_data.get('Month', 'Current Month')}",
                    value=f"${cost_data.get('Cost (USD)', 0):.2f}",
                    delta=None
                )
            
            with col2:
                st.info(f"Period: {cost_data.get('Period', 'N/A')}")
        else:
            if cost_data.get("Error") == "Cost Explorer not enabled":
                st.warning("⚠️ Cost Explorer Not Enabled")
                st.info(cost_data.get("Message", "Cost Explorer needs to be enabled."))
                
                if "Instructions" in cost_data:
                    st.markdown("**Instructions:**")
                    for instruction in cost_data["Instructions"]:
                        st.markdown(f"- {instruction}")
                    
                    st.markdown("**Note:** Cost Explorer activation can take up to 24 hours after enabling.")
            else:
                st.error(f"Error loading cost data: {cost_data.get('Error', 'Unknown error')}")
    
    with tab2:
        st.subheader("Cost by Service")
        
        with st.spinner("Loading service costs..."):
            service_costs = get_cost_by_service()
        
        if service_costs and "Error" not in service_costs[0]:
            df = pd.DataFrame(service_costs)
            
            # Create bar chart
            fig = px.bar(
                df,
                x='Service',
                y='Cost (USD)',
                title='AWS Cost by Service',
                labels={'Cost (USD)': 'Cost (USD)', 'Service': 'AWS Service'}
            )
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
            
            # Display table
            st.dataframe(df, use_container_width=True)
        else:
            if service_costs and service_costs[0].get("Error") == "Cost Explorer not enabled":
                st.warning("⚠️ Cost Explorer Not Enabled")
                st.info(service_costs[0].get("Message", "Cost Explorer needs to be enabled."))
                st.markdown("Please enable Cost Explorer in AWS Billing Console and wait 24 hours for activation.")
            else:
                st.warning("No service cost data available.")
                if service_costs and "Error" in service_costs[0]:
                    st.error(service_costs[0]["Error"])
    
    with tab3:
        st.subheader("Daily Cost Trend")
        
        days = st.slider("Number of days to show:", 7, 90, 30)
        
        with st.spinner("Loading daily costs..."):
            daily_costs = get_daily_costs(days)
        
        if daily_costs and "Error" not in daily_costs[0]:
            df = pd.DataFrame(daily_costs)
            df['Date'] = pd.to_datetime(df['Date'])
            
            # Create line chart
            fig = px.line(
                df,
                x='Date',
                y='Cost (USD)',
                title=f'Daily AWS Costs (Last {days} days)',
                labels={'Cost (USD)': 'Cost (USD)', 'Date': 'Date'}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Show summary statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Average Daily Cost", f"${df['Cost (USD)'].mean():.2f}")
            with col2:
                st.metric("Total Period Cost", f"${df['Cost (USD)'].sum():.2f}")
            with col3:
                st.metric("Max Daily Cost", f"${df['Cost (USD)'].max():.2f}")
        else:
            st.warning("No daily cost data available.")
            if daily_costs and "Error" in daily_costs[0]:
                st.error(daily_costs[0]["Error"])
    
    with tab4:
        st.subheader("Cost Forecast")
        
        with st.spinner("Loading cost forecast..."):
            forecast = get_cost_forecast()
        
        if "Error" not in forecast:
            st.metric(
                label="30-Day Forecast",
                value=f"${forecast.get('Forecasted Cost (USD)', 0):.2f}",
                delta=None
            )
            st.info(f"Forecast Period: {forecast.get('Forecast Period', 'N/A')}")
        else:
            st.error(f"Error loading forecast: {forecast.get('Error', 'Unknown error')}")

# Deploy Page
elif menu == "🚀 Deploy":
    st.header("🚀 Infrastructure Deployment")
    
    # Check Terraform status first
    terraform_status = get_terraform_status()
    
    if terraform_status.get('terraform_available'):
        st.success(f"✅ Terraform Available: {terraform_status.get('version', 'Unknown version')}")
        
        if terraform_status.get('initialized'):
            st.success("✅ Terraform Initialized")
        else:
            st.warning("⚠️ Terraform not initialized. Please run 'terraform init' first.")
    else:
        st.error(f"❌ Terraform not available: {terraform_status.get('error', 'Unknown error')}")
        st.stop()
    
    st.markdown("""
    **Infrastructure Components:**
    
    This deployment will create the following AWS resources:
    - 🔧 **Lambda Function**: Demo function for CloudWatch logs
    - 🗄️ **S3 Bucket**: Secure storage with encryption and versioning
    - 📊 **CloudWatch Log Group**: For Lambda function logs
    - 🚨 **CloudWatch Alarm**: Monitor Lambda function errors
    - 🔐 **IAM Role**: With appropriate permissions for Lambda
    """)
    
    # Current Infrastructure Status
    st.subheader("📋 Current Infrastructure Status")
    
    with st.spinner("Checking current infrastructure status..."):
        state_info = get_terraform_state()
    
    if state_info.get('success'):
        if state_info.get('resources', 0) > 0:
            st.info(f"📦 **Deployed Resources**: {state_info.get('resources')} resources currently deployed")
            
            # Show deployed resources
            with st.expander("View Deployed Resources"):
                for resource in state_info.get('resource_list', []):
                    st.write(f"- {resource}")
            
            # Show outputs if available
            outputs_info = get_terraform_outputs()
            if outputs_info.get('success'):
                st.subheader("📤 Infrastructure Outputs")
                outputs = outputs_info.get('outputs', {})
                
                col1, col2 = st.columns(2)
                with col1:
                    if 'lambda_function_name' in outputs:
                        st.metric("Lambda Function", outputs['lambda_function_name']['value'])
                    if 's3_bucket_name' in outputs:
                        st.metric("S3 Bucket", outputs['s3_bucket_name']['value'])
                
                with col2:
                    if 'aws_region' in outputs:
                        st.metric("AWS Region", outputs['aws_region']['value'])
                    if 'aws_account_id' in outputs:
                        st.metric("AWS Account", outputs['aws_account_id']['value'])
        else:
            st.info("🆕 No infrastructure currently deployed")
    else:
        st.warning(f"⚠️ Could not check infrastructure status: {state_info.get('error', 'Unknown error')}")
    
    st.markdown("---")
    
    # Deployment Actions
    st.subheader("🚀 Deployment Actions")
    
    # Create columns for different actions
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🔍 Plan**")
        st.markdown("Preview changes before applying")
        if st.button("� Plan Infrastructure", type="secondary", use_container_width=True):
            with st.spinner("Generating Terraform plan..."):
                plan_result = trigger_terraform("plan")
                
                if plan_result.get('success'):
                    st.success("✅ Plan generated successfully!")
                    st.text_area("Plan Output", plan_result.get('output', ''), height=300)
                else:
                    st.error(f"❌ Plan failed: {plan_result.get('error', 'Unknown error')}")
    
    with col2:
        st.markdown("**🚀 Deploy**")
        st.markdown("Apply the infrastructure changes")
        if st.button("🚀 Deploy Infrastructure", type="primary", use_container_width=True):
            # First run plan
            with st.spinner("Planning deployment..."):
                plan_result = trigger_terraform("plan")
                
                if not plan_result.get('success'):
                    st.error(f"❌ Planning failed: {plan_result.get('error', 'Unknown error')}")
                else:
                    # Show plan summary
                    st.info("📋 Plan completed. Proceeding with deployment...")
                    
                    # Then apply
                    with st.spinner("Deploying infrastructure... This may take several minutes."):
                        apply_result = trigger_terraform("apply")
                        
                        if apply_result.get('success'):
                            st.success("🎉 Infrastructure deployed successfully!")
                            st.balloons()
                            
                            # Show outputs
                            st.text_area("Deployment Output", apply_result.get('output', ''), height=200)
                            
                            # Refresh page data
                            st.rerun()
                        else:
                            st.error(f"❌ Deployment failed: {apply_result.get('error', 'Unknown error')}")
                            st.text_area("Error Details", apply_result.get('output', ''), height=200)
    
    with col3:
        st.markdown("**🗑️ Destroy**")
        st.markdown("Remove all deployed resources")
        
        # Add confirmation for destroy
        if 'destroy_confirmed' not in st.session_state:
            st.session_state.destroy_confirmed = False
        
        if not st.session_state.destroy_confirmed:
            if st.button("🗑️ Destroy Infrastructure", type="secondary", use_container_width=True):
                st.session_state.destroy_confirmed = True
                st.rerun()
        else:
            st.warning("⚠️ This will destroy all resources!")
            col_confirm, col_cancel = st.columns(2)
            
            with col_confirm:
                if st.button("✅ Confirm Destroy", type="secondary", use_container_width=True):
                    with st.spinner("Destroying infrastructure... This may take several minutes."):
                        destroy_result = trigger_terraform("destroy")
                        
                        if destroy_result.get('success'):
                            st.success("✅ Infrastructure destroyed successfully!")
                            st.text_area("Destroy Output", destroy_result.get('output', ''), height=200)
                            st.session_state.destroy_confirmed = False
                            st.rerun()
                        else:
                            st.error(f"❌ Destroy failed: {destroy_result.get('error', 'Unknown error')}")
                            st.text_area("Error Details", destroy_result.get('output', ''), height=200)
                            st.session_state.destroy_confirmed = False
            
            with col_cancel:
                if st.button("❌ Cancel", use_container_width=True):
                    st.session_state.destroy_confirmed = False
                    st.rerun()
    
    # Additional Information
    st.markdown("---")
    st.subheader("ℹ️ Deployment Information")
    
    with st.expander("📖 What gets deployed?"):
        st.markdown("""
        **AWS Resources Created:**
        
        1. **Lambda Function** (`cloudops-demo-function`)
           - Runtime: Python 3.9
           - Timeout: 30 seconds
           - Purpose: Generate logs for monitoring
        
        2. **S3 Bucket** (`cloudops-demo-bucket-[random]`)
           - Versioning enabled
           - Server-side encryption (AES256)
           - Public access blocked
        
        3. **CloudWatch Log Group** (`/aws/lambda/cloudops-demo-function`)
           - Retention: 7 days
           - For Lambda function logs
        
        4. **CloudWatch Alarm** (`cloudops-demo-function-errors`)
           - Monitors Lambda errors
           - Threshold: 5 errors in 5 minutes
        
        5. **IAM Role** (`cloudops-demo-function-role`)
           - Basic Lambda execution permissions
           - CloudWatch logging permissions
        
        **Estimated Cost:** Free Tier eligible (within AWS limits)
        """)
    
    with st.expander("🔧 Troubleshooting"):
        st.markdown("""
        **Common Issues:**
        
        - **"Access Denied"**: Check your AWS credentials and IAM permissions
        - **"Bucket already exists"**: S3 bucket names must be globally unique
        - **"Timeout"**: Large deployments may take time, please wait
        - **"Terraform not found"**: Ensure Terraform is installed and in PATH
        
        **Required AWS Permissions:**
        - IAM: Create roles and policies
        - Lambda: Create and manage functions
        - S3: Create and manage buckets
        - CloudWatch: Create log groups and alarms
        """)
    
    st.markdown("---")
    st.markdown("💡 **Tip**: Use the Plan action first to preview changes before deploying!")

# Monitoring Page
elif menu == "📈 Monitoring":
    st.header("📈 CloudWatch Monitoring")
    
    st.subheader("CloudWatch Logs")
    
    # Get available log groups
    available_log_groups = list_available_log_groups()
    
    if available_log_groups:
        # Create options for selectbox
        log_group_options = [group["name"] for group in available_log_groups]
        
        # Add our known log groups if they're not already there
        known_groups = ["/aws/lambda/cloudops-demo-function", "/aws/lambda/test-function"]
        for group in known_groups:
            if group not in log_group_options:
                log_group_options.append(group)
        
        log_group = st.selectbox(
            "Select Log Group:",
            log_group_options,
            index=0
        )
        
        # Show log group info
        selected_group_info = next((g for g in available_log_groups if g["name"] == log_group), None)
        if selected_group_info:
            st.info(f"📊 Log group size: {selected_group_info['size_bytes']} bytes")
    else:
        # Fallback to manual entry
        log_group = st.text_input(
            "Enter Log Group Name:",
            value="/aws/lambda/cloudops-demo-function",
            help="Enter the CloudWatch log group name"
        )
        st.info("💡 Tip: Deploy the demo infrastructure first to create log groups.")
    
    # Number of log lines
    lines = st.slider("Number of log lines:", 10, 1000, 100)
    
    # Add Lambda trigger option
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔍 Fetch Logs"):
            with st.spinner("Fetching CloudWatch logs..."):
                logs = get_logs(log_group, lines)
            
            if logs and not logs.startswith("Error") and not logs.startswith("No logs") and not logs.startswith("Log group"):
                st.success(f"✅ Found logs for {log_group}")
                st.text_area("Logs", logs, height=400)
                
                # Download logs
                st.download_button(
                    label="📥 Download Logs",
                    data=logs,
                    file_name=f"cloudwatch_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
            else:
                st.warning("No logs found or failed to connect.")
                if logs:
                    st.info(logs)
                    
                    # Provide helpful suggestions
                    if "does not exist" in logs:
                        st.markdown("""
                        **💡 Suggestions:**
                        - Check if the log group name is correct
                        - Deploy the demo infrastructure first
                        - Make sure the Lambda function has been executed
                        """)
                    elif "no log events" in logs:
                        st.markdown("""
                        **💡 To generate logs:**
                        - Use the "Test Lambda" button to generate logs
                        - Or go to AWS Console → Lambda → cloudops-demo-function
                        - Click "Test" to create and run a test event
                        - Return here and fetch logs again
                        """)
    
    with col2:
        if st.button("🚀 Test Lambda (Generate Logs)"):
            if log_group == "/aws/lambda/cloudops-demo-function":
                with st.spinner("Triggering Lambda function..."):
                    result = trigger_lambda_function("cloudops-demo-function")
                
                if result["success"]:
                    st.success("✅ Lambda function executed successfully!")
                    st.json(result["response"])
                    st.info("💡 Lambda logs may take 10-30 seconds to appear. Wait a moment, then click 'Fetch Logs'.")
                    
                    # Add a small countdown/timer suggestion
                    import time
                    with st.spinner("⏱️ Logs are being processed... (wait 15 seconds)"):
                        time.sleep(15)
                    st.success("✅ You can now fetch the logs!")
                else:
                    st.error(f"❌ Failed to trigger Lambda: {result['error']}")
            else:
                st.warning("Lambda trigger only works for 'cloudops-demo-function'")
    
    # Show available log groups
    if available_log_groups:
        with st.expander("📋 Available Log Groups"):
            for group in available_log_groups:
                st.write(f"• {group['name']} ({group['size_bytes']} bytes)")
    else:
        st.info("🔍 No log groups found. Make sure you have the right permissions.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; margin-top: 2rem;'>
        <p>🧠 CloudOps Toolkit - Built with ❤️ using Streamlit & AWS</p>
        <p>For support, visit our <a href='https://github.com/lukeperry/CloudOps-toolkit'>GitHub repository</a></p>
    </div>
    """,
    unsafe_allow_html=True
)
