
import logging
import os
import mysql.connector


class SQLHelper:

    def __init__(self):
        logging.info('init sql helper')

    def create_sql_db(self, host='localhost', user='test_user', passwd='password'):
        mydb = mysql.connector.connect(host=host, user=user, passwd=passwd)
        return mydb

