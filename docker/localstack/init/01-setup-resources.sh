#!/bin/bash

# LocalStack initialization script for LocalStack UI resources
set -e

echo "Setting up LocalStack resources for LocalStack UI..."

# Wait for LocalStack to be ready
awslocal s3 ls || echo "Waiting for LocalStack..."

# Create S3 buckets for testing
echo "Creating S3 buckets..."
awslocal s3 mb s3://demo-bucket-1
awslocal s3 mb s3://demo-bucket-2
awslocal s3 mb s3://test-uploads

# Add some test files to buckets
echo "Adding test files to buckets..."
echo "Hello World" >/tmp/hello.txt
echo "Sample document content" >/tmp/sample.txt
echo '{"test": "data"}' >/tmp/data.json

awslocal s3 cp /tmp/hello.txt s3://demo-bucket-1/hello.txt
awslocal s3 cp /tmp/sample.txt s3://demo-bucket-1/docs/sample.txt
awslocal s3 cp /tmp/data.json s3://demo-bucket-2/data.json

# Create sample Lambda functions
echo "Creating Lambda functions..."

# Create a simple Python function
cat >/tmp/lambda_function.py <<'EOF'
def lambda_handler(event, context):
    return {
        'statusCode': 200,
        'body': f'Hello from Lambda! Event: {event}'
    }
EOF

zip -j /tmp/function.zip /tmp/lambda_function.py

awslocal lambda create-function \
	--function-name hello-world \
	--runtime python3.9 \
	--role arn:aws:iam::000000000000:role/lambda-role \
	--handler lambda_function.lambda_handler \
	--zip-file fileb:///tmp/function.zip \
	--description "Simple hello world function"

# Create another function with different configuration
awslocal lambda create-function \
	--function-name data-processor \
	--runtime python3.11 \
	--role arn:aws:iam::000000000000:role/lambda-role \
	--handler lambda_function.lambda_handler \
	--zip-file fileb:///tmp/function.zip \
	--description "Data processing function" \
	--timeout 30 \
	--memory-size 256

# Create Step Functions state machines
echo "Creating Step Functions state machines..."

# Simple state machine
cat >/tmp/simple_state_machine.json <<'EOF'
{
  "Comment": "A simple minimal example",
  "StartAt": "Hello",
  "States": {
    "Hello": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:000000000000:function:hello-world",
      "End": true
    }
  }
}
EOF

awslocal stepfunctions create-state-machine \
	--name "SimpleExample" \
	--definition file:///tmp/simple_state_machine.json \
	--role-arn "arn:aws:iam::000000000000:role/StepFunctionsRole"

# More complex state machine
cat >/tmp/complex_state_machine.json <<'EOF'
{
  "Comment": "Data processing workflow",
  "StartAt": "ProcessData",
  "States": {
    "ProcessData": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:000000000000:function:data-processor",
      "Next": "CheckResult"
    },
    "CheckResult": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.status",
          "StringEquals": "success",
          "Next": "Success"
        }
      ],
      "Default": "Failure"
    },
    "Success": {
      "Type": "Succeed"
    },
    "Failure": {
      "Type": "Fail",
      "Error": "ProcessingFailed",
      "Cause": "Data processing failed"
    }
  }
}
EOF

awslocal stepfunctions create-state-machine \
	--name "DataProcessingWorkflow" \
	--definition file:///tmp/complex_state_machine.json \
	--role-arn "arn:aws:iam::000000000000:role/StepFunctionsRole"

# Clean up temporary files
rm -f /tmp/hello.txt /tmp/sample.txt /tmp/data.json
rm -f /tmp/lambda_function.py /tmp/function.zip
rm -f /tmp/simple_state_machine.json /tmp/complex_state_machine.json

echo "LocalStack initialization complete!"
echo "S3 buckets: demo-bucket-1, demo-bucket-2, test-uploads"
echo "Lambda functions: hello-world, data-processor"
echo "Step Functions: SimpleExample, DataProcessingWorkflow"
