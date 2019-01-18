import pymysql
import os
import json
import boto3
# from botocore.vendored import requests
import cfnresponse


def handler(event, context):
    print(event)
    try:
        if event['RequestType'] == 'Create' or event['RequestType'] == 'Update':
            print("Create or Update")
            
            host = event["ResourceProperties"]["DBHost"]
            print(host)
            user = event["ResourceProperties"]["DBUser"]
            print(user)
            password = event["ResourceProperties"]["DBPassword"]
            print(password)
            # db = event["ResourceProperties"]["DBName"]
            db = ""
            print(db)
            
           
            # Connect to the database
            connection = pymysql.connect(host=host, user=user, password=password, db=db,
                                         charset='utf8mb4',
                                         cursorclass=pymysql.cursors.DictCursor)
            print("Connection built")

            with connection.cursor() as cursor:
                cursor.execute("CREATE DATABASE IF NOT EXISTS test;")
                sql = """
                       CREATE TABLE IF NOT EXISTS test.accounts (
                       item_id int(11) unsigned NOT NULL AUTO_INCREMENT,
                       name varchar(100) DEFAULT NULL,
                       PRIMARY KEY (item_id))
                       ENGINE=InnoDB DEFAULT CHARSET=latin1;"""
                cursor.execute(sql)
                connection.commit()
                print("Table created")
                
                cursor.execute("INSERT INTO test.accounts (1, `car`)")
                cursor.execute("INSERT INTO test.accounts (2, `teddy bear`)")
                cursor.execute("INSERT INTO test.accounts (3, `knife`)")
                connection.commit()
                print("Records Inserted")
                connection.close()
                
            respond_cloudformation(event, context)
            return
        else:
            respond_cloudformation(event, context)
            return
    except:
        respond_cloudformation(event, context)

def respond_cloudformation(event, context, data=None):
    responseBody = {
        'Reason': 'See the details in CloudWatch Log Stream',
        'PhysicalResourceId': 'Custom Lambda Function',
        'StackId': event['StackId'],
        'RequestId': event['RequestId'],
        'LogicalResourceId': event['LogicalResourceId'],
        'Data': data
    }

    print('Response = ' + json.dumps(responseBody))
    cfnresponse.send(event, context, cfnresponse.SUCCESS)
    
