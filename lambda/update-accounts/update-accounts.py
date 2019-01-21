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


    items = json.loads(event["body"])

    try:
        with connection.cursor() as cursor:
            for item in items:
                cursor.execute("SELECT * FROM test.accounts where item_id = %s" %item["item_id"])
                result = [row for row in cursor]
                # If item in the table then update, otherwise insert
                if result != []:
                    update(item, cursor)
                else:
                    insert(item, cursor)
                connection.commit()

        return make_response("200", {"code":"200", "message":"Successful insert or update"})

    except Exception as e:
        print(e)
        # return status failed
        return make_response("400",{"code":"500", "message":"Failed insert and update"})
    finally:
        connection.close()

# insert single item
def insert(item, cursor):
    print("Insert")
    cursor.execute("INSERT INTO test.accounts (item_id, name) VALUES (%s,'%s')" %(item["item_id"], item["name"]))


# update single item
def update(item, cursor):
    print("Update")
    cursor.execute("UPDATE test.accounts set name = '%s' where item_id = %s" %(item["name"],item["item_id"]))


def make_response(statusCode, body):
	response ={
		"isBase64Encoded" : "true",
		"statusCode": statusCode,
		"headers": {'Content-Type': 'application/json'},
		"body": json.dumps(body)
	}
	return response
