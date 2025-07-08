from . import mysql
import MySQLdb.cursors

def get_db_cursor(dict_cursor=True):
    if dict_cursor:
        return mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    return mysql.connection.cursor() 