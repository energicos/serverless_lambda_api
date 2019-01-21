# Single API with Lambda Backend

Create Restful API on AWS with serverless architecture using AWS Lambda, AWS ApiGateway, AWS Cognito. The Restful API execute CRUD operations on RDS Mysql.



## Intro

- we are going to make a simple RESTful API with the following two endpoints:
  - **POST /users/${userId}/hello** / the request body will be saved in a DynamoDB table. In this tutorial, the request body must have this structure: `{ "email": "any@email.com" }`
  - **GET /users/${userId}/hello**/ the response will contain the value for `"email"` set in the POST request.

(This is a placeholder for an architecture graph)

## Deployment Environment

* AWS EC2-AMI (with awscli installed)
* AdminRole
* Install pip (https://docs.aws.amazon.com/cli/latest/userguide/install-linux.html)

(This can be replaced with a Docker container)

## 1. create a zip file for lambda code

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
./upload_lambda.sh
```



- now upload it to an s3 bucket

```shell
aws s3 cp account_index.zip s3://${account_id}-bucketname/lambdaone/account_index.zip
# like
aws s3 cp account_index.zip s3://300746241447-invoicegenerator-lambdacode/lambdaone/account_index.zip
```

## Delete all stacks

'''shell

aws cloudformation delete-stack --stack-name tests3 --region eu-central-1
'''


## 2. Upload Swagger files

- we need to upload the Swagger file to an S3 Bucket
- go to the directory where the swagger files are located and sync the directory content

```shell
  # Modify your bucket name with the correct AWS account ID
$ aws s3 sync . s3://300746241447-invoicegenerator-swaggerapis
```


-------------------------------------------------------------


## 3. Launch the  Stack

```shell
$ aws cloudformation create-stack \
--stack-name api-lambda-stack \
--template-body file://test.yaml \
--capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_NAMED_IAM CAPABILITY_IAM
```

- to update the stack
- make sure the zip files on the Lambdacode Bucket is up-to-date
- then

```shell
$ aws cloudformation update-stack \
--stack-name api-lambda-stack \
--template-body file://test.yaml \
--capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_NAMED_IAM CAPABILITY_IAM
```





## 4. Parameter

- only the usual Variables

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



## 5. Resources

![](C:\Users\balerion\git\software.dev.notes\aws\images\lambdaapi.png)

### 5.1 API Gateway Ressources

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



### 5.2 Lambda Resources

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



### 5.3 Dynamo DB Resources

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





## 6. Test the API

### 6.1 check the POST Endpoint

- go to the Console - API Gateways
- check if the API Gateway is hooked up to Lambda by selecting the **POST** option under **/users** and then clicking **TEST**
- now we enter some testdata
- on the Test page set
  - **userId** = 123,
  - **Request Body**

```json
{
    "email": "myfancy@gmail.com"
}
```

- now click **Test**
- If everything worked, the **Status** should be **200** with no data



### 6.2 check the GET Endpoint

- check to see if your data was saved by going to the /hello GET Test page and trying a request
- set **userId** to 123
- the response body should contain the Request Body from the POST test
