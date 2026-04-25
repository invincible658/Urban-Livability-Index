import pymysql

try:
    conn = pymysql.connect(host='localhost', user='root', password='nakul@1978')
    print('connected ok')
    conn.close()
except Exception as e:
    print('Failed:', str(e))
