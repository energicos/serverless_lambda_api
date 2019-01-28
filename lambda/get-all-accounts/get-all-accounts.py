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
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM test.accounts")
            # return status success
            body = [row for row in cursor]
        print(body)
        return make_response("200", body)
    except Exception as e:
        # return status failed
        return make_response("500", {"code": "500", "message": "Error getting items"})
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
