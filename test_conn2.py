import mysql.connector

try:
    conn = mysql.connector.connect(host='localhost', user='root', password='nakul@1978')
    print('connected successfully')
    conn.close()
except Exception as e:
    print('Failed:', str(e))
