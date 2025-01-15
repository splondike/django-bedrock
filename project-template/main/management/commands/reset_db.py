"""
Destroys the database after ending all database sessions.

Modified from https://github.com/django-extensions/django-extensions and edited slightly
"""

import logging

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

import psycopg as Database


class Command(BaseCommand):
    help = "Resets the database for this project."

    def handle(self, *args, **options):
        """
        Reset the database for this project.

        Note: Transaction wrappers are in reverse as a work around for
        autocommit, anybody know how to do this the right way?
        """

        database = "default"

        dbinfo = settings.DATABASES.get(database)
        if dbinfo is None:
            raise CommandError("Unknown database %s" % database)

        engine = dbinfo.get("ENGINE")

        user = password = database_name = database_host = database_port = ""
        if engine == "mysql":
            (user, password, database_name, database_host, database_port) = parse_mysql_cnf(dbinfo)

        user = dbinfo.get("USER")
        password = dbinfo.get("PASSWORD")
        owner = user

        database_name = dbinfo.get("NAME")
        if database_name == "":
            raise CommandError("You need to specify DATABASE_NAME in your Django settings file.")

        database_host = dbinfo.get("HOST") or database_host
        database_port = dbinfo.get("PORT") or database_port

        conn_params = {"dbname": "template1"}
        if user:
            conn_params["user"] = user
        if password:
            conn_params["password"] = password
        if database_host:
            conn_params["host"] = database_host
        if database_port:
            conn_params["port"] = database_port

        connection = Database.connect(**conn_params)
        connection.autocommit = True
        cursor = connection.cursor()

        # Kick off all the existing users
        close_sessions_query = """
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '%s';
        """ % database_name
        logging.info("Executing... '%s'", close_sessions_query.strip())
        try:
            cursor.execute(close_sessions_query)
        except Database.ProgrammingError as e:
            logging.exception("Error: %s", str(e))

        drop_query = "DROP DATABASE \"%s\";" % database_name
        logging.info("Executing... '%s'", drop_query)
        try:
            cursor.execute(drop_query)
        except Database.ProgrammingError as e:
            logging.exception("Error: %s", str(e))

        create_query = "CREATE DATABASE \"%s\"" % database_name
        if owner:
            create_query += " WITH OWNER = \"%s\" " % owner
        create_query += " ENCODING = 'UTF8'"

        if settings.DEFAULT_TABLESPACE:
            create_query += " TABLESPACE = %s;" % settings.DEFAULT_TABLESPACE
        else:
            create_query += ";"

        logging.info("Executing... '%s'", create_query)
        cursor.execute(create_query)
