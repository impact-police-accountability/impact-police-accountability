"""Fetch lawyer data from S3 and pack it into a DB, probably then export to """

import csv
import time

import psycopg2
import psycopg2.extras
import psycopg2.sql

from config import DBAUTH, get_bucket
from import_lawyer_data_from_s3 import ensure_schema
from sql_helpers import import_table


def get_args():
    parser = argparse.ArgumentParser(description=__doc__)
    return vars(parser.parse_args())


def main():
    with psycopg2.connect(**DBAUTH) as conn:
        conn.cursor_factory = psycopg2.extras.RealDictCursor
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS geodata")
        cursor.execute(
            """
            CREATE TABLE geodata (
                zipcode text,
                city text,
                state_abbr text,
                latitude double precision,
                longitude double precision
            )
            """
        )
        tablename = "geodata"
        filepath = "data/us-zip-code-latitude-and-longitude.csv"
        import_table(cursor, tablename, filepath, delimiter=";")
        conn.commit()


if "__main__" == __name__:
    main()
