import inspect
import sqlite3
import traceback
from datetime import datetime
from sqlite3 import Connection, OperationalError
from time import sleep
from typing import Type

import mysql.connector
from mysql.connector import MySQLConnection
import pandas as pd
from peewee import Model, IntegrityError, FloatField, IntegerField, CharField, DateTimeField
from playhouse.migrate import migrate, SchemaMigrator
from playhouse.sqlite_ext import JSONField

from Colors import printc
from Files import run_cmd
from Strings import quote
from Times import now


# TODO with peewee

def mysql_connect_remote() -> MySQLConnection:
    # a temp whatever database
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


def get_column_names_old(connection, table_name: str):
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


def remove_column(connection, table_name, column_name, debug=False):
    try:
        if debug:
            print(r"ALTER TABLE {} DROP COLUMN {}".format(table_name, column_name))
        connection.execute("ALTER TABLE {} DROP COLUMN {}".format(table_name, column_name))
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


def default_naming_convention_table(model: Model):
    return model.__name__.upper()

# todo Model Type[Model], replace table model or db connection

# noinspection PyProtectedMember
def get_database(model: Model):
    return model._meta.database

# noinspection PyProtectedMember
def get_all_models(model: Model):
    return model.get_models()

# noinspection PyProtectedMember
def get_all_tables(model: Model):
    return model.get_tables()


# noinspection PyProtectedMember
def get_table_name(model: Type[Model]):
    return model._meta.table_name


def get_columns_name_db(connection, model: Type[Model]):
    query = "select * from {} LIMIT 0;".format(get_table_name(model).lower())
    cursor = connection.cursor()
    cursor.execute(query)
    return [desc[0] for desc in cursor.description]


def get_columns_name_model(model: Type[Model]):
    return list(model._meta.fields)


# noinspection PyProtectedMember
def print_model_infos(model: Model):
    database = model._meta.database
    table_name = model._meta.table_name
    primary_key = model._meta.primary_key
    fields = model._meta.fields
    list(map(print, (database, table_name, primary_key, fields)))


def fill_rows(model: Type[Model], columns_order: list[str], values: list[list[object]] | list[object], debug=True,
              raise_if_exist=False):
    """ columns_order's names have to be the field name and not the column name. |columns_order|=|values| """
    if type(values[0]) != list:
        values = [values]
    db_columns = get_columns_name_model(model)
    indexes_to_ignore = [columns_order.index(index) for index in set(columns_order) - set(db_columns)]
    columns_order = [column for column in columns_order if column in db_columns]
    rows = [dict(zip(columns_order,
                     [value[i] for i in range(len(value)) if i not in indexes_to_ignore])) for value in values]
    try:
        q = model.insert_many(rows)  # q = model.select().where(model.executed == 0)
        q.execute()
    except Exception as e:  # todo peewee.OperationalError: database is locked
        print("database may be locked", traceback.format_exc(), "sleep(1) & retry function")
        if "order_id" in rows:
            rows["order_id"] += 0.1
        sleep(1)
        return fill_rows(model, columns_order, values, debug, raise_if_exist)
    #     if raise_if_exist:
    #         traceback.format_exc()
    #         raise IntegrityError
    #     else:
    #         return
    if debug:
        printc("{} {}".format(now(), q.sql()), color="black")


def type_to_field(val: object):
    python_type = type(val)
    if python_type is str and str(val).isdecimal():
        python_type = float
    if python_type is str:
        return CharField(null=True)
    elif python_type is int:
        return IntegerField(null=True)
    elif python_type is float:
        return FloatField(null=True)
    elif python_type is datetime:
        return DateTimeField(null=True)
    elif python_type in [list, tuple, dict]:
        return JSONField(json_dumps=val, null=True)
    else:
        raise TypeError(str(python_type) + " is not defined")


def add_missing_columns_to_db(model, columns, columns_type=[str | list], debug=True):
    """ Update the Model code after adding columns """
    database = get_database(model)
    db_columns = get_columns_name_db(model)
    column_name = get_columns_name_model(model)
    migrator = SchemaMigrator(database)
    for i in range(len(columns)):
        column = columns[i].replace("-", "_")
        column_type = columns_type[i] if type(columns_type) is list else columns_type
        if column in db_columns:
            continue
        migrate(migrator.add_column(column_name, column, type_to_field(column_type)))
    if debug:
        run_cmd("python -m pwiz -e sqlite {}".format(get_database(model)))


def column_order_copy_past_into_code(model, columns_order):
    model_code_lines = list(inspect.getsource(model).replace("    ", "").split("\n"))
    n = 0
    for column in columns_order:
        for line in model_code_lines:
            words = line.split()
            if column == words[0]:
                print(line)
                n += 1
                break
    print(n)


def get_dict_fields_name_n_value(model) -> dict:
    return model.__dict__["__data__"]


def get_dataframe(model):
    return pd.DataFrame(list(model.select().dicts()))
