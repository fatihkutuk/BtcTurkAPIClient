import time
import math
import mysql.connector
from mysql.connector import (connection)

def mysql_connect():
    con = connection.MySQLConnection(user='root', password='',
                                host='localhost',
                                database='btc')
    return con
def get_last_exchange():
    con = mysql_connect()
    cursor = con.cursor()
    query = ("SELECT * FROM exchanges  order by id desc limit 2617")   
    cursor.execute(query) 
    result = cursor.fetchall()
    total = 0
    avg = 0
    for x in result:
       total = float(total) + float(x[2])
    avg = total/2617
    return avg   
    con.commit()
    cursor.close()
    con.close()   

