Serverless API Gateway with RDS

Table of Contents Serverless API Gateway with RDS1. Background Info2. Scope of delivery3. Details of the assignment4. Technology Stack5. Code repository6. Provided by us7. Timeline



1. Background Info

- we are developing a microservice-based Business Platform running solely on AWS
- all our deployments are Cloudformation based, we dont deploy Resources into Dev/ Prod Environment via Console
- the stacks are being launched using AWSCLI Commands
- to connect to the backend resources we implement a “multi-API-Gateway under on domain” - approach involving basepathmapping in our Cloudformation stacks 
- the API-Gateway configuration is being delivered by a Swagger (OpenAPI) file which is being uploaded onto an s3 bucket and used during stack deployment as source for the API definition
- the API access is being secured by a Cognito based Authorizer which uses a Cognito pool (Cognito stack)



2. Scope of delivery

  Results                 	Description                             
  Documentation           	A documentation describing the resources and the approach as well as the elaborations on the lambda/ nodejs code
  Cloudformation templates	Cloudformation templates with the resources working as expected in an automated way (rds, lambda, cognito, Api Gateway, IAM)
  nodejs index.js         	indexjs files containing the code for the lambda functions



3. Details of the assignment

- the goal is to create a Cloudformation stack/ nested stack 
- the stacks must be created as yaml files
- the stack shall allow serverless CRUD operations on a RDS (mariaDB) resource acting as backend
- the stack(s) shall deploy an API Gateway which allows us to add, update, delete, and search for accounts using a Swagger API definition loaded from an s3 bucket (see example below)

      Api:
        Type: AWS::ApiGateway::RestApi
        Properties:
          Description: .....
          Name: !Ref RestApiName
          ApiKeySourceType: !Ref ApiKeySourceType
          Body:
            Fn::Transform:
              Name: AWS::Include
              Parameters:
                Location: !Sub "s3://bucketname/swagger.yaml"
          EndpointConfiguration:
            Types:
              - !Ref EndpointConfiguration
          FailOnWarnings: true
          MinimumCompressionSize: !Ref minimumCompressionSize

- the API Gateway must be secured via Cognito User Pool
- the Cognito-based Authorizer shall be embedded into the Swagger Definition and being used on the methods GET, POST, PUT, DELETE for the Lambda-path
- create a skeleton framework for the API, with the paths and methods needed to accomplish the basics of reading and writing data
- the data shall be stored in a RDS (MySQL), and served up via Lambda functions, through the API Gateway
- use a simple accounts database, consisting of 2 tables
  - accounts
  - user
- the tables shall be build with an SQL script like the following using Lambda and Cloudformation (after the stack has created the RDS Resource)

    CREATE TABLE `accounts` (
      `item_id` int(11) unsigned NOT NULL AUTO_INCREMENT,
      `name` varchar(100) DEFAULT NULL,
      PRIMARY KEY (`account_id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=latin1;

- the business logic shall be setup in AWS Lambda for reading, and writing data to the relational database
- create Lambda functions based on a node.js runtime
- create one lambda function for each method and make each method work properly with the Lambda function
- we want to have the basic CRUD operations for the API
  - the ability to get all records from the database (Search accounts)
  - be able to insert new records (add accounts)
  - be able to get a single record (get accounts)
  - be able to update a single record (update accounts)
  - be able to delete records (delete accounts)



4. Technology Stack

The following technologies are mandatory and cannot be replaced by any other technology similar or not without our explicit approval:

- Devops-Technologies
  - AWS API Gateway as the API layer
  - AWS Cognito
  - AWS Lambda
  - AWS RDS MySQL
  - Node.js as runtime for the lambda function of this API
  - alernatively pthon 3 as runtime 
  - OpenAPI definition
  - postman to check the API



5. Code repository

- we provide a repository named "serverless_api_rds"
- Fork the repository and work inside your own account
- Give access to jprivillaso@gmail.com and aerioeus@gmail.com so we can track your work
- arrange your code like this

    --api-masterstack
      |__api_rds.yaml
    --nodejs
      |__index.js
    --swaggerapis
      |__swagger.yaml

- Create a Pull Request and we will review the code





6. Provided by us

- Documentation template as reference
- Github Repository to pull from



7. Timeline

- Project Start: 16.01.2019
- Project due date:  23.01.2019

