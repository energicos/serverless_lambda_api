aws lambda create-function --function-name test-create-table --runtime python3.6 --role "arn:aws:iam::624008370141:role/LambdaRole" --handler "create-table-rds.handler" --code S3Bucket=tests3-s3bucket-t9ne2v3mb47y,S3Key=create-table-rds.zip --region eu-central-1