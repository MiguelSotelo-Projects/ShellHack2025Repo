# Google ADK Setup Guide

This guide will help you set up Google Cloud Platform configuration for the Ops Mesh Backend ADK agent system.

## 🚀 Quick Setup

### Option 1: Automated Setup (Recommended)

Run the automated setup script:

```bash
python setup_google_adk.py
```

This script will:
- ✅ Check Google Cloud CLI installation
- ✅ List and select your Google Cloud project
- ✅ Enable required APIs
- ✅ Create service account with proper permissions
- ✅ Generate service account key
- ✅ Create configuration file (.env)
- ✅ Test the configuration

### Option 2: Manual Setup

If you prefer to set up manually or the automated script doesn't work:

## 📋 Prerequisites

### 1. Google Cloud CLI

Install Google Cloud CLI if not already installed:

**macOS:**
```bash
brew install google-cloud-sdk
```

**Linux:**
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

**Windows:**
Download from: https://cloud.google.com/sdk/docs/install

### 2. Authentication

Login to Google Cloud:
```bash
gcloud auth login
```

Set your project:
```bash
gcloud config set project YOUR_PROJECT_ID
```

## 🔧 Manual Configuration Steps

### 1. Enable Required APIs

Enable the following APIs in your Google Cloud project:

```bash
gcloud services enable aiplatform.googleapis.com
gcloud services enable pubsub.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable logging.googleapis.com
gcloud services enable monitoring.googleapis.com
```

### 2. Create Service Account

Create a service account for the application:

```bash
gcloud iam service-accounts create ops-mesh-agent \
    --display-name="Ops Mesh Agent Service Account" \
    --description="Service account for Ops Mesh hospital operations system"
```

### 3. Assign Required Roles

Assign the following roles to your service account:

```bash
PROJECT_ID="your-project-id"
SERVICE_ACCOUNT="ops-mesh-agent@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/pubsub.admin"

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/storage.admin"

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/logging.logWriter"

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/monitoring.metricWriter"

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/monitoring.viewer"
```

### 4. Create Service Account Key

Generate and download the service account key:

```bash
gcloud iam service-accounts keys create ops-mesh-service-account.json \
    --iam-account=ops-mesh-agent@${PROJECT_ID}.iam.gserviceaccount.com
```

### 5. Create Environment File

Create a `.env` file in the project root:

```bash
# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_REGION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=/path/to/ops-mesh-service-account.json

# Ops Mesh Configuration
OPS_MESH_TOPIC_PREFIX=ops-mesh
OPS_MESH_MONITORING=true
OPS_MESH_LOGGING=true

# Database Configuration
DATABASE_URL=sqlite:///./ops_mesh.db

# API Configuration
API_V1_STR=/api/v1
PROJECT_NAME=Ops Mesh Backend

# Development Settings
DEBUG=true
RELOAD=true
```

### 6. Set Environment Variables

Export the environment variables:

```bash
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_REGION="us-central1"
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/ops-mesh-service-account.json"
```

## 🧪 Testing Configuration

### Test Google Cloud Libraries

```python
# Test script
import os
from google.cloud import pubsub_v1, storage, logging
from google.cloud import monitoring_v3
import google.cloud.aiplatform

# Set credentials
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/path/to/ops-mesh-service-account.json'
os.environ['GOOGLE_CLOUD_PROJECT'] = 'your-project-id'

# Test clients
try:
    storage_client = storage.Client()
    print("✅ Storage client works")
    
    publisher = pubsub_v1.PublisherClient()
    print("✅ Pub/Sub client works")
    
    logging_client = logging.Client()
    print("✅ Logging client works")
    
    monitoring_client = monitoring_v3.MetricServiceClient()
    print("✅ Monitoring client works")
    
    aiplatform.init(project='your-project-id', location='us-central1')
    print("✅ AI Platform works")
    
    print("🎉 All Google Cloud services configured correctly!")
    
except Exception as e:
    print(f"❌ Error: {e}")
```

### Test Agent System

```bash
# Start the agent system
python start_agents.py
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Authentication Errors

**Error**: `google.auth.exceptions.DefaultCredentialsError`

**Solution**:
- Verify `GOOGLE_APPLICATION_CREDENTIALS` points to valid key file
- Check service account has required permissions
- Ensure key file is not corrupted

#### 2. API Not Enabled

**Error**: `403 Forbidden` or `API not enabled`

**Solution**:
```bash
gcloud services enable [API_NAME]
```

#### 3. Insufficient Permissions

**Error**: `403 Forbidden` or permission denied

**Solution**:
- Check service account roles
- Verify project ID is correct
- Ensure service account is active

#### 4. Project Not Found

**Error**: `Project not found`

**Solution**:
- Verify project ID is correct
- Check if project exists and is accessible
- Ensure billing is enabled

### Debug Commands

```bash
# Check current project
gcloud config get-value project

# List available projects
gcloud projects list

# Check authentication
gcloud auth list

# Test service account
gcloud auth activate-service-account --key-file=ops-mesh-service-account.json

# Check APIs
gcloud services list --enabled

# Check service account permissions
gcloud projects get-iam-policy YOUR_PROJECT_ID
```

## 📊 Cost Considerations

### Free Tier Limits

Google Cloud provides free tier limits for:
- **Pub/Sub**: 10GB/month free
- **Cloud Storage**: 5GB/month free
- **Cloud Logging**: 50GB/month free
- **Cloud Monitoring**: 150MB/month free
- **AI Platform**: Limited free usage

### Estimated Costs

For a small hospital system:
- **Pub/Sub**: ~$5-10/month
- **Cloud Storage**: ~$2-5/month
- **Cloud Logging**: ~$5-15/month
- **Cloud Monitoring**: ~$2-5/month
- **AI Platform**: ~$10-50/month (depending on usage)

**Total estimated cost**: $25-85/month

### Cost Optimization Tips

1. **Use Pub/Sub efficiently**: Batch messages when possible
2. **Optimize logging**: Use appropriate log levels
3. **Monitor usage**: Set up billing alerts
4. **Use regional resources**: Choose appropriate regions
5. **Clean up resources**: Remove unused topics and subscriptions

## 🔒 Security Best Practices

### 1. Service Account Security

- **Least Privilege**: Only assign necessary roles
- **Key Rotation**: Rotate service account keys regularly
- **Access Control**: Limit who can access service account keys
- **Monitoring**: Monitor service account usage

### 2. Network Security

- **VPC**: Use Virtual Private Cloud for network isolation
- **Firewall**: Configure appropriate firewall rules
- **Private Google Access**: Use private endpoints when possible

### 3. Data Protection

- **Encryption**: All data encrypted in transit and at rest
- **Access Logs**: Enable audit logging
- **Data Retention**: Set appropriate retention policies

## 📚 Additional Resources

### Documentation

- [Google Cloud AI Platform](https://cloud.google.com/ai-platform/docs)
- [Google Cloud Pub/Sub](https://cloud.google.com/pubsub/docs)
- [Google Cloud Storage](https://cloud.google.com/storage/docs)
- [Google Cloud Logging](https://cloud.google.com/logging/docs)
- [Google Cloud Monitoring](https://cloud.google.com/monitoring/docs)

### Support

- [Google Cloud Support](https://cloud.google.com/support)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/google-cloud-platform)
- [Google Cloud Community](https://cloud.google.com/community)

## 🎯 Next Steps

After completing the setup:

1. **Test the configuration**: Run `python start_agents.py`
2. **Start the API server**: Run `python run.py`
3. **Monitor the system**: Check Google Cloud Console
4. **Set up monitoring**: Configure alerts and dashboards
5. **Scale as needed**: Adjust resources based on usage

## 📞 Getting Help

If you encounter issues:

1. **Check the logs**: Look at agent system logs
2. **Verify configuration**: Run the test script
3. **Check Google Cloud Console**: Look for errors in the console
4. **Review this guide**: Ensure all steps were completed
5. **Contact support**: Use Google Cloud support channels

---

**Happy coding! 🚀**
