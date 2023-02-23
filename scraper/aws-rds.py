import pymysql

#db instance identifier: database-1
#username: admin
#password: PythonAws2023
#port: 3306
#host: database-1.cm0g4ldq4qxz.eu-west-2.rds.amazonaws.com

db = pymysql.connect(host="database-1.cm0g4ldq4qxz.eu-west-2.rds.amazonaws.com", user="admin", password="PythonAws2023")
cursor = db.cursor()

