import mysql.connector

try:
    connection = mysql.connector.connect(host=89.46.111.71,
                                         database='Sql1244824_2',
                                         user='Sql1244824',
                                         password='l8t3550281')

    #mySql_insert_query = """INSERT INTO Laptop (Id, Name, Price, Purchase_date) 
                           #VALUES 
                           #(15, 'Lenovo ThinkPad P71', 6459, '2019-08-14') """

    mySql_insert_query = """INSERT INTO consumo (casa, data, kwatt) VALUES ('Lavinio 71', '2023-09-29', 151)"""
    cursor = connection.cursor()
    cursor.execute(mySql_insert_query)
    connection.commit()
    print(cursor.rowcount, "Record inserted successfully into Laptop table")
    cursor.close()

except mysql.connector.Error as error:
    print("Failed to insert record into Laptop table {}".format(error))

finally:
    if connection.is_connected():
        connection.close()
        print("MySQL connection is closed")
