# Single API with Lambda Backend

Create Restful API on AWS with serverless architecture using AWS Lambda, AWS ApiGateway, AWS Cognito. The Restful API execute CRUD operations on RDS Mysql.

## ToDO:

* Echo database password
* EnvironmentName prefix
* Enhancement (vpc, subnet, SecurityGroup)
* Enhancement lambda code and api error message


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


## 3. Launch RDS  Stack

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

## 4. Launch API Stack

```shell
cd api-masterstack
aws cloudformation create-stack \
--stack-name testapi \
--template-body file://api.yml \
--parameters ParameterKey=S3BucketName,ParameterValue=${BucketName} \
--capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_NAMED_IAM CAPABILITY_IAM \
--region eu-central-1
```

aws cognito-idp initiate-auth --auth-flow USER_PASSWORD_AUTH --client-id 187u2dsdnpnr6rpbkau4dss5ig	 --auth-parameters USERNAME=test,PASSWORD=Abcd12345% --region eu-central-1

# response to the challenge
aws cognito-idp admin-respond-to-auth-challenge --user-pool-id eu-central-1_CbzHpSukN --client-id 187u2dsdnpnr6rpbkau4dss5ig  --challenge-name NEW_PASSWORD_REQUIRED --challenge-responses USERNAME=test,NEW_PASSWORD=Abcd12345% --session m8AC3YUQblXSyRbWje1BT1FNsHUnjH_GEPmpWwxKkfaYZtnyIhQvvbM9NShcT_HPa1_y-ovS710BKYIaC7g4E2byN4FL-d__W87DdsvpqaM8-RuCAxsmp96OLQ7kYjKIXoPuhYTcsgrx_0sbRTIdqQSc4-fhsxgYw9GjEw8e1-8SzGvIdPir-t-6pPR5at80BZnVOxC2Ad7AIb7DQdrHRybAjBtG1QZKpY0tm6kmuIDGqltwRM2ZK3YuTt_edqWm8niYP9abBzCgz0da_JzMEuuqzUIkc7_AmY2T66B8e9CdClsS5X3mGWjYHZJX6pJPWLOd8vwtZ7suLH3u9O7NnqqNM_ceD6baVomAULw2YqoWULct9vZf2DGp23FbjiOGqoFBoo0TvKQKmIGYK9BOVm0dASUBZEFUmHfcXKC3vWOarAB7nbWHg3X_gNQgVmPBRrsdWrUU4SskRtZhrEsHhbJ9wR0_touCLTVDaO0dpgl-rNiIfONPf1ErPWQUZYdUeZSG5UFARsEl9AhXAA5onwfeM2zXWygF_pjYMKergLgnbDNTmMES1MrkEVLp-C8jcSI3c9-EMSbRMXuUqkjHomTGtvhO74k16dAYAcw9fz0EvoEJgv5RSHVVH_mwEvjizAxidOEgmlLiQslhvQsLwZh1wj5g-kscnlJMWcVR2lJwcNX8ZfTBHk1eOzVJYa7Du1V9deGkK0d68D3F6apyNDt44wC3G9RMcVU0ErxDIIg_KEfHm04EKFWqe1BAE7PyjGz01i-HxBh4YDBelFjdOXnt-PpCEWEWQ0lw1kFAjPzDv57yiQNTccG0MOAEUsa5 --region eu-central-1







## 5. Parameter

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


## 6. Resources

![](C:\Users\balerion\git\software.dev.notes\aws\images\lambdaapi.png)

### 6.1 API Gateway Ressources

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



### 6.2 Lambda Resources

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



### 6.3 Dynamo DB Resources

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


## 7. Test the API

### 7.1 check the POST Endpoint

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



### 7.2 check the GET Endpoint

- check to see if your data was saved by going to the /hello GET Test page and trying a request
- set **userId** to 123
- the response body should contain the Request Body from the POST test



curl -H "Content-Type: application/json" -H "Authorization: eyJraWQiOiJneVYralFGSmsrc2xJZFd3OCtjbHFoTGMwc0JUNG9MZGNKT3pzTW8xbE93PSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiIwNzI0NTI5Zi0yYmFmLTRjZjAtYTI3Yi04YmRjZDVkYzNjODUiLCJldmVudF9pZCI6ImZmYTJhN2Q3LTFlNjktMTFlOS04NmZlLTFmMGIzOGM2OWY0NCIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiYXdzLmNvZ25pdG8uc2lnbmluLnVzZXIuYWRtaW4iLCJhdXRoX3RpbWUiOjE1NDgxNzc2MjIsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC5ldS1jZW50cmFsLTEuYW1hem9uYXdzLmNvbVwvZXUtY2VudHJhbC0xX0NiekhwU3VrTiIsImV4cCI6MTU0ODE4MTIyMiwiaWF0IjoxNTQ4MTc3NjIyLCJqdGkiOiI4NTJkN2IyOC03YWU3LTRmYWUtOGJiNy1iOGE4MWMwMmE0MzUiLCJjbGllbnRfaWQiOiIxODd1MmRzZG5wbnI2cnBia2F1NGRzczVpZyIsInVzZXJuYW1lIjoidGVzdCJ9.EXJkIWP6AwAL-n7fODfcObvOjjokGKnupB1uqOx4-t_cBTZB8tTwGl1GNcYnmt5xghf-a12UebbaamxjBSPzNhQpgfOVdsd3U6Ni6F3oRWv3sUg36bBs6asQm60iDfPuG3X_SFU9ElDnQ11ki9qGHnCC3WZgaFN3BYF_1rwOmgA63ktoprPDArpzuDr2nIfCG5itJzSdHKJGpTJfU_qKyHmkhmNSYtr0m3IBNv3b4FDo0G7l4nij3m0kAlmC8Q78J5X_pFGoELxDiliykqWdLhkvKVItp1v8ufapnZwhes70pZwJVy0rNaP37-6aNkHTvX3zxJ9tPTlVcPvy0TRvww" https://xpjo63jxj6.execute-api.eu-central-1.amazonaws.com/prd/accounts/items


## Delete all stacks

'''shell
# delete rds stack
aws cloudformation delete-stack --stack-name testrds --region eu-central-1
# must delete all files before the deletion of s3 bucket
aws cloudformation delete-stack --stack-name tests3 --region eu-central-1
'''
