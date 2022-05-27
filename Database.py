import sqlite3
from sqlite3 import Connection, OperationalError
from time import sleep

import mysql.connector
from mysql.connector import MySQLConnection

from Strings import quote
from Times import now


def mysql_connect_remote() -> MySQLConnection:
    HOST = "remotemysql.com"
    DATABASE = "6fLyxUf3eM"
    USER = "6fLyxUf3eM"
    password = 'IhNaLib2PI'
    try:
        connection = mysql.connector.connect(host=HOST, database=DATABASE, user=USER, password=password, buffered=True)
    except mysql.connector.errors.DatabaseError:
        sleep(30)
        return mysql_connect_remote()
    return connection


def is_mysql(connection) -> bool:
    state = False
    if "mysql.connector.connection" in str(type(connection)):
        state = True
        mysql_reset_buffer(connection)
    return state


def mysql_reset_buffer(connection, c=None):
    try:
        connection.reconnect()
    except Exception as err:
        if "Unread result found" in str(err):
            if c:
                c.fetchall()


def create_table(request: str, connection: Connection):
    cursor = connection.cursor()
    cursor.execute(request)


def create_table_profit(connection: Connection):
    request = """CREATE TABLE IF NOT EXISTS PROFIT (
                    amount_token FLOAT,
                    fee_amount FLOAT,
                    xp FLOAT,
                    token TEXT,
                    fee TEXT,
                    style TEXT,
                    date DATE
              );"""
    create_table(request, connection)


def insert(connection: Connection, table_name, values, columns, debug=False):
    if debug:
        print("INSERT OR IGNORE INTO {} ({}) VALUES ({})"
              .format(table_name, ", ".join(columns), ",".join(map(quote, values))))
    connection.execute("INSERT OR IGNORE INTO {} ({}) VALUES ({})"
                       .format(table_name, ", ".join(columns), ",".join(map(quote, values))))


def get_column_names(connection, table_name: str):
    column_names = []
    if is_mysql(connection):
        cursor = connection.cursor(buffered=True)
        cursor.execute("""SELECT * FROM {}""".format(table_name))
        column_names = cursor.column_names
    else:
        cursor = connection.cursor()
        for tuples in cursor.execute("PRAGMA table_info({})".format(table_name)):
            column_names.append(tuples[1])
    return column_names


def add_column(connection, table_name, column_name, data_type, debug=False):
    try:
        if debug:
            print("ALTER TABLE {} ADD {} {}".format(table_name, column_name, data_type))
        connection.execute(r"ALTER TABLE {} ADD {} {}".format(table_name, column_name, data_type))
    except OperationalError:
        pass


def insert_or_update(connection, table_name, values, columns,
                     primary_keys: list = None, primary_key_values: list = None,
                     pre_update_date=False, is_update=False, debug=False, commit=False):
    try:
        if len(columns) == 0 or len(values) == 0:
            raise ValueError("len is 0")
        if debug:
            print("\tINSERT INTO {} ({}) VALUES ({})"
                  .format(table_name, ", ".join(columns), ",".join(map(quote, values))))
        if is_update:
            raise sqlite3.IntegrityError
        query = "INSERT INTO {} ({}) VALUES ({})".format(table_name, ", ".join(columns), ",".join(map(quote, values)))
        if is_mysql(connection):
            connection.cmd_query(query)
        else:
            connection.execute(query)
    except sqlite3.IntegrityError:
        new_columns = columns
        new_values = values
        if not pre_update_date:
            # action on supprime l'indice de la date
            date_index = columns.index('date')
            # new_columns = columns[:date_index] + columns[date_index + 1:]
            # new_values = values[:date_index] + values[date_index + 1:]
            values[date_index] = now()
        set_pattern = ", ".join((new_columns[i] + " = " + quote(new_values[i]) for i in range(len(new_values))))
        keys_constraint = "WHERE "
        for i in range(len(primary_keys)):
            primary_key, primary_key_value = primary_keys[i], primary_key_values[i]
            keys_constraint += primary_key + " = " + quote(primary_key_value) + " and "
        keys_constraint = keys_constraint[:-5]
        if debug:
            print("""\tUPDATE {}\nSET {}\n{}""".format(table_name, set_pattern, keys_constraint))
        query = """UPDATE {}\nSET {}\n{}""".format(table_name, set_pattern, keys_constraint)
        if is_mysql(connection):
            connection.cmd_query(query)
        else:
            connection.execute(query)
    if commit:
        connection.commit()
