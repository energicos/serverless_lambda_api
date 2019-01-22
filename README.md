# Single API with Lambda Backend

Create Restful API on AWS with serverless architecture using AWS Lambda, AWS ApiGateway, AWS Cognito. The Restful API execute CRUD operations on RDS Mysql.

## ToDO:

* Echo database password
* EnvironmentName prefix
* Enhancement (vpc, subnet, SecurityGroup)
* Enhancement lambda code and api error message
* Tagging
* Advanced Feature: triggering lambda with custom resource
* Advanced Feature: custom cognito client lambda


## Intro


(This is a placeholder for an architecture graph)

## 1. Deployment Environment

* AWS EC2-AMI (with awscli installed)
* AdminRole
* Install pip (https://docs.aws.amazon.com/cli/latest/userguide/install-linux.html)

(This can be replaced with a Docker container)

## 2. Create S3 Stack and Upload files

- now create an s3 bucket

```shell
cd api-masterstack/
aws cloudformation create-stack --stack-name tests3 --template-body file://s3.yml --region eu-central-1
```

- go to the directory where the root of lambda file is stored
- zip and upload all lambda deployment package

```shell
# get bucketName
export BucketName=$(aws cloudformation list-exports --query "Exports[?Name==\`BucketName\`].Value" --no-paginate --output text --region eu-central-1)
cd lambda/
# zip and upload all lambdas into the bucket
./upload_lambda.sh $BucketName
```

- upload swagger file and cf yml into s3 bucket

```shell
cd swaggerapis
aws s3 cp swagger.yml s3://${BucketName}
cd api-masterstack
aws s3 cp . s3://${BucketName}  --recursive --include "*.yml"
```


## 3. Launch RDS Stack

```shell
cd api-masterstack
aws cloudformation create-stack \
--stack-name testrds \
--template-body file://rds.yml \
--parameters ParameterKey=S3BucketName,ParameterValue=${BucketName} \
--capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_NAMED_IAM CAPABILITY_IAM \
--region eu-central-1
```

- populate the rds tables with create-table-rds function

```shell
export LambdaArn=$(aws cloudformation list-exports --query "Exports[?Name==\`testrds-CreateTableRDSLambdaArn\`].Value" --no-paginate --output text --region eu-central-1)
aws lambda invoke --function-name ${LambdaArn} output.txt --region eu-central-1
rm output.txt
```

## 4. Launch API Stack (testapi Stack)

```shell
cd api-masterstack
aws cloudformation create-stack \
--stack-name testapi \
--template-body file://api.yml \
--parameters ParameterKey=S3BucketName,ParameterValue=${BucketName} \
--capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_NAMED_IAM CAPABILITY_IAM \
--region eu-central-1
```

- get Endpoint from the deployed api, call it invoke_url

```shell
# for example
export invoke_url=https://t6xvekq3yf.execute-api.eu-central-1.amazonaws.com/Dev
```

- get user_pool_id and user_pool_client_id

```shell
export user_pool_id=$(aws cloudformation list-exports --query "Exports[?Name==\`testapi-UserPoolId\`].Value" --no-paginate --output text --region eu-central-1)
export user_pool_client_id=$(aws cloudformation list-exports --query "Exports[?Name==\`testapi-UserPoolClientId\`].Value" --no-paginate --output text --region eu-central-1)
```

- create user for testing

```shell
export username=test
aws cognito-idp admin-create-user --user-pool-id ${user_pool_id} --username ${username} --temporary-password Abcd12345% --region eu-central-1
```

- response to challenge

```shell
export session=$(aws cognito-idp initiate-auth --auth-flow USER_PASSWORD_AUTH --client-id ${user_pool_client_id} --auth-parameters USERNAME=${username#,PASSWORD=Abcd12345% --query 'Session' --output text --region eu-central-1)
```


```shell
# Be Careful! This is not idempotent
# response to the challenge
aws cognito-idp admin-respond-to-auth-challenge --user-pool-id ${user_pool_id} --client-id ${user_pool_client_id}  --challenge-name NEW_PASSWORD_REQUIRED --challenge-responses USERNAME=${username},NEW_PASSWORD=Abcd12345% --session ${session} --region eu-central-1
```

- get IdToken

```shell
export id_token=$(aws cognito-idp initiate-auth --auth-flow USER_PASSWORD_AUTH --client-id ${user_pool_client_id} --auth-parameters USERNAME=${username},PASSWORD=Abcd12345%  --region eu-central-1 --query "AuthenticationResult.IdToken" --output text)
```

## 5. check the API

(The id_token can expire! in which case you have to reaquire a id_token)

- Test GetAllAccounts

```shell
curl -H "Content-Type: application/json" -H "Authorization: ${id_token}" ${invoke_url}/accounts/items

# result:
'''shell
[{"item_id": 1, "name": "car"}, {"item_id": 2, "name": "teddy bear"}, {"item_id": 3, "name": "knife"}]
```

- Test SearchAccounts

```shell
curl -H "Content-Type: application/json" -H "Authorization: ${id_token}" ${invoke_url}/accounts/items?id=1
```

- Test UpdateAccount

```shell
curl -X PUT -H "Content-Type: application/json" -H "Authorization: ${id_token}" -d '[{"item_id":1,"name":"update"}]' ${invoke_url}/accounts/items

# result:
{"code": "200", "message": "Successful insert or update"}
```

- you can get the updated value

```shell
curl -H "Content-Type: application/json" -H "Authorization: ${id_token}" ${invoke_url}/accounts/item?id=1

# result:
[{"item_id": 1, "name": "update"}]
```

- insert value:

'''shell
curl -X PUT -H "Content-Type: application/json" -H "Authorization: ${id_token}" -d '[{"item_id":4,"name":"insert"}]' ${invoke_url}/accounts/items

# result:
{"code": "200", "message": "Successful insert or update"}
'''

- get the inserted value

```shell
curl -H "Content-Type: application/json" -H "Authorization: ${id_token}" ${invoke_url}/accounts/item?id=4
# result
[{"item_id": 4, "name": "insert"}]
```

- Test delete Accounts

```shell
curl -X DELETE -H "Content-Type: application/json" -H "Authorization: ${id_token}" ${invoke_url}/accounts/item?id=4
# result
{"code": "200", "message": "Delete Success"}
```

- try to get the deleted item

```shell
curl -H "Content-Type: application/json" -H "Authorization: ${id_token}" ${invoke_url}/accounts/item?id=4
# result
[]
```

## 6. Parameter

```yaml
Parameters:
  Owner:
    Description: Enter Team or Individual Name Responsible for the Stack.
    Type: String
    Default: Andreas Rose

  Project:
    Description: Enter Project Name.
    Type: String
    Default: invoicegenerator

  Subproject:
    Description: Enter Project Name.
    Type: String
    Default: ebs

  EnvironmentName:
    Description: An environment name that will be prefixed to resource names
    Type: String
    Default: Dev
    AllowedValues:
      - Dev
      - Prod
    ConstraintDescription: Specify either Dev or Prod
```


## 7. Resources

![](C:\Users\balerion\git\software.dev.notes\aws\images\lambdaapi.png)

### 7.1 API Gateway Ressources

- at first we need an api gateway ressource
- it pulls its ressources (methods etc) from a swagger file sitting in an s3 bucket, which we uploaded before

```yaml
  MyApiGateway:
    Type: AWS::ApiGateway::RestApi
    Properties:
      Name: !Sub "${AWS::StackName}-MyApiGateway"
      Description: A description
      FailOnWarnings: true
      Body:
        Fn::Transform:
          Name: AWS::Include
          Parameters:
            Location: !Sub "s3://${AWS::AccountId}-${Project}-swaggerapis/lambda1_swagger.yaml"
```

- now we need a deployment for the api gateway

```yaml
  MyApiGatewayDeployment:
    Type: AWS::ApiGateway::Deployment
    Properties:
      RestApiId: !Ref MyApiGateway
      StageName: prod
```

- and finally the appropriate IAM Service Role for the API Gateway resource
- it allows the apigateway resource to invoke Lambda functions

```yaml
  MyApiGatewayRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: apigateway.amazonaws.com
            Action: sts:AssumeRole
      Policies:
        - PolicyName: InvokeLambda
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - lambda:InvokeFunction
                Resource:
                  - !GetAtt HelloLambda.Arn
```



### 7.2 Lambda Resources

- we first create the function
- it pulls its code from an s3 bucket

```yaml
  HelloLambda:
    Type: AWS::Lambda::Function
    Properties:
      Role: !GetAtt HelloLambdaRole.Arn  # TODO
      Handler: index.handleHttpRequest
      Runtime: nodejs6.10
      Environment:
        Variables:
          HELLO_DB: !Sub "arn:aws:dynamodb:${AWS::Region}:*:table/${HelloTable}"
      Code:
        S3Bucket:
          Fn::ImportValue: !Sub ${EnvironmentName}-LambdaCodeBucket-Name
        S3Key: lambdaone/account_index.zip
```

- now we need the Lambda policy to allow logging

```yaml
 # Policy required for all lambda function roles.
  BaseLambdaExecutionPolicy:
    Type: AWS::IAM::ManagedPolicy
    Properties:
      Description: Base permissions needed by all lambda functions.
      PolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Action:
              - logs:CreateLogGroup
              - logs:CreateLogStream
              - logs:PutLogEvents
              - ec2:CreateNetworkInterface
              - ec2:DescribeNetworkInterfaces
              - ec2:DeleteNetworkInterface
            Resource: "*"
```

- after that we create the case-specific Service role for Lambda

```yaml
  HelloLambdaRole:  # -> AppAPIRole
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: lambda.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - !Ref BaseLambdaExecutionPolicy
      Policies:
        - PolicyName: getHello
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - dynamodb:GetItem
                Resource: !Sub "arn:aws:dynamodb:${AWS::Region}:*:table/${HelloTable}"
        - PolicyName: putHello
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - dynamodb:PutItem
                Resource: !Sub "arn:aws:dynamodb:${AWS::Region}:*:table/${HelloTable}"
```



### 7.3 Dynamo DB Resources

- finally we create the Dynamo Table

```yaml
  HelloTable:
    Type: AWS::DynamoDB::Table
    Properties:
      ProvisionedThroughput:
        ReadCapacityUnits: 5
        WriteCapacityUnits: 5
      AttributeDefinitions:
        - AttributeName: user_id
          AttributeType: S
      KeySchema:
        - AttributeName: user_id
          KeyType: HASH
```


## 8. Delete all stacks

```shell
# delete api stack
aws cloudformation delete-stack --stack-name testapi --region eu-central-1
# delete rds stack
aws cloudformation delete-stack --stack-name testrds --region eu-central-1
# must delete all files before the deletion of s3 bucket
aws cloudformation delete-stack --stack-name tests3 --region eu-central-1
```
