"""Fetch lawyer data from S3 and pack it into a DB, probably then export to """

import csv
import time

import psycopg2
import psycopg2.extras
import psycopg2.sql

from config import DBAUTH
from import_lawyer_data_from_s3 import ensure_schema
from sql_helpers import import_table


def get_args():
    parser = argparse.ArgumentParser(description=__doc__)
    return vars(parser.parse_args())


def main():
    start_time = time.time()
    with psycopg2.connect(**DBAUTH) as conn:
        print("Got a connection...")
        conn.cursor_factory = psycopg2.extras.RealDictCursor
        ensure_schema(conn)
        cursor = conn.cursor()

        def get_filepath(tablename):
            return "data/{tablename}/{tablename}.csv".format(tablename=tablename)

        import_table(cursor, "law_firms", get_filepath("law_firms"))
        import_table(cursor, "lawyers", get_filepath("lawyers"))
        # truncate zipcodes to 5
        cursor.execute(
            "UPDATE law_firms SET zipcode = LEFT(zipcode, 5) WHERE zipcode != LEFT(zipcode, 5)"
        )
        cursor.execute("""CREATE INDEX ON law_firms USING HASH (zipcode)""")
        conn.commit()


if "__main__" == __name__:
    main()
