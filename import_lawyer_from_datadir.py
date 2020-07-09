"""Fetch lawyer data from S3 and pack it into a DB, probably then export to """

import csv
import time

import psycopg2
import psycopg2.extras
import psycopg2.sql

from config import DBAUTH, get_bucket
from import_lawyer_data_from_s3 import ensure_schema


def get_args():
    parser = argparse.ArgumentParser(description=__doc__)
    return vars(parser.parse_args())


def import_table(cursor, tablename):
    # there are _so many_ assumptions here...
    # need to get the columns from the table definition
    table_ident = psycopg2.sql.Identifier(tablename)
    cursor.execute(psycopg2.sql.SQL("SELECT * FROM {} WHERE FALSE").format(table_ident))
    colnames = [c.name for c in cursor.description]

    # construct insert statement
    insert_statement = "INSERT INTO {{tablename}} ({{cols}}) VALUES ({placeholders})".format(
        placeholders=", ".join("%({})s".format(c) for c in colnames)
    )
    stmt_as_sql = psycopg2.sql.SQL(insert_statement).format(
        tablename=table_ident,
        cols=psycopg2.sql.SQL(", ").join(psycopg2.sql.Identifier(c) for c in colnames),
    )
    with open("data/{tablename}/{tablename}.csv".format(tablename=tablename)) as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            cursor.execute(stmt_as_sql, row)


def main():
    bucket = get_bucket()
    done = 0
    start_time = time.time()
    with psycopg2.connect(**DBAUTH) as conn:
        conn.cursor_factory = psycopg2.extras.RealDictCursor
        ensure_schema(conn)
        cursor = conn.cursor()
        import_table(cursor, "law_firms")
        import_table(cursor, "lawyers")
        conn.commit()


if "__main__" == __name__:
    main()
