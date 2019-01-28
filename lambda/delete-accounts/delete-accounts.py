import pymysql
import os
import json

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

    item_id = event["queryStringParameters"]["id"]

    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE from test.accounts where item_id= %s" %item_id)
            connection.commit()

        return make_response("200", {"code":"200", "message": "Delete Success"})
    except Exception as e:
        return make_response("404",{"code":"404", "message": "Delete Failed"})
    finally:
        connection.close()


def make_response(statusCode, body):
	response ={
		"isBase64Encoded" : "true",
		"statusCode": statusCode,
		"headers": {'Content-Type': 'application/json'},
		"body": json.dumps(body)
	}
	return response
