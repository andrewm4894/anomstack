# Amazon Web Services Integration

This directory contains integrations for Amazon Web Services (AWS) used by Anomstack.

## Services Supported

### Amazon S3 (`s3.py`)
- **Purpose**: Store and retrieve trained ML models in S3 buckets
- **Features**:
  - Upload/download trained anomaly detection models
  - Model versioning and organization
  - Secure access with IAM credentials
  - Bucket management and lifecycle policies
  - Server-side encryption support

### Authentication (`credentials.py`)
- **Purpose**: Manage AWS authentication and credentials
- **Features**:
  - AWS credentials management (access keys, IAM roles)
  - Session token handling
  - Cross-service credential sharing
  - Support for multiple authentication methods

## Setup Requirements

### 1. AWS Account Setup
- Create an AWS account with appropriate billing setup
- Enable S3 service in your preferred region

### 2. IAM User/Role Setup
Create an IAM user or role with S3 permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::your-anomstack-bucket",
                "arn:aws:s3:::your-anomstack-bucket/*"
            ]
        }
    ]
}
```

### 3. S3 Bucket Creation
Create a dedicated S3 bucket for Anomstack models:

```bash
# Using AWS CLI
aws s3 mb s3://your-anomstack-models-bucket --region us-east-1

# Set up bucket versioning (optional but recommended)
aws s3api put-bucket-versioning \
    --bucket your-anomstack-models-bucket \
    --versioning-configuration Status=Enabled
```

### 4. Configuration

Set environment variables:

```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"
export S3_BUCKET_NAME="your-anomstack-models-bucket"
```

Alternative authentication methods:
- **IAM Roles**: For EC2 instances or ECS containers
- **AWS CLI Profile**: Using `aws configure` with named profiles
- **Instance Profile**: For applications running on EC2

## Usage Examples

### S3 Configuration
In your metric batch YAML file:

```yaml
model_store: s3
model_store_params:
  bucket_name: "your-anomstack-models-bucket"
  prefix: "models/"
  region: "us-east-1"
```

### Advanced Configuration
```yaml
model_store: s3
model_store_params:
  bucket_name: "your-anomstack-models-bucket"
  prefix: "models/production/"
  region: "us-east-1"
  encryption: "AES256"
  storage_class: "STANDARD_IA"
```

## Model Storage Structure

Models are stored in S3 with the following structure:
```
s3://your-bucket/
├── models/
│   ├── metric_batch_name/
│   │   ├── metric_name/
│   │   │   ├── model_YYYYMMDD_HHMMSS.pkl
│   │   │   ├── metadata_YYYYMMDD_HHMMSS.json
│   │   │   └── ...
│   │   └── ...
│   └── ...
```

## Security Best Practices

1. **Use IAM Roles**: Prefer IAM roles over access keys when possible
2. **Least Privilege**: Grant only necessary S3 permissions
3. **Bucket Policies**: Implement bucket-level access controls
4. **Encryption**: Enable server-side encryption for sensitive model data
5. **VPC Endpoints**: Use VPC endpoints for private communication
6. **Access Logging**: Enable S3 access logging for audit trails

## Cost Optimization

- **Storage Classes**: Use appropriate storage classes (Standard, IA, Glacier)
- **Lifecycle Policies**: Automatically transition old models to cheaper storage
- **Compression**: Models are automatically compressed before upload
- **Cleanup**: Regularly clean up old model versions

Example lifecycle policy:
```json
{
    "Rules": [{
        "Status": "Enabled",
        "Transitions": [{
            "Days": 30,
            "StorageClass": "STANDARD_IA"
        }, {
            "Days": 90,
            "StorageClass": "GLACIER"
        }]
    }]
}
```

## Troubleshooting

### Common Issues

1. **Access Denied**: Check IAM permissions and bucket policies
2. **Bucket Not Found**: Verify bucket name and region
3. **Slow Uploads**: Consider using multipart upload for large models
4. **Connection Timeouts**: Check network connectivity and retry logic

### Debugging

Enable debug logging:
```python
import logging
logging.getLogger('boto3').setLevel(logging.DEBUG)
logging.getLogger('botocore').setLevel(logging.DEBUG)
```

### Performance Monitoring

Monitor S3 performance using:
- AWS CloudWatch metrics
- S3 access logs
- AWS X-Ray tracing (if enabled)
