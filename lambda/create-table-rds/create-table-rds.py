import pymysql
import os
import json
import boto3

def handler(event, context):
    print(event)
    host = os.environ['DBEndpoint']
    user = os.environ['DBUser']
    password = os.environ['DBPassword']
    db = ""
    # Connect to the database
    connection = pymysql.connect(host=host, user=user, password=password, db=db,
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    print("Connection built")
    try:
        with connection.cursor() as cursor:
            cursor.execute("CREATE DATABASE IF NOT EXISTS test;")
            sql = """
                  CREATE TABLE IF NOT EXISTS test.accounts (
                  item_id int(11) unsigned NOT NULL AUTO_INCREMENT,
                  name varchar(100) DEFAULT NULL,
                  PRIMARY KEY (item_id))
                  ENGINE=InnoDB DEFAULT CHARSET=latin1;
                  """
            cursor.execute(sql)
            connection.commit()
            print("Table created")
                
            cursor.execute("INSERT INTO test.accounts (item_id, name) VALUES (1, 'car')")
            cursor.execute("INSERT INTO test.accounts (item_id, name) VALUES (2, 'teddy bear')")
            cursor.execute("INSERT INTO test.accounts (item_id, name) VALUES (3, 'knife')")
            connection.commit()
            print("Records Inserted")
    finally:
        connection.close()
