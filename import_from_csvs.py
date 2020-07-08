"""Import law enforcement agency information from CSVs in the data dir."""
import argparse
import csv
import os
import re
import time

import psycopg2
import psycopg2.extras

from config import DBAUTH


def import_one_state(cursor, filepath):
    with open(filepath) as fh:
        print("Importing data for {}...".format(filepath))
        reader = csv.DictReader(fh)
        i = 0
        for i, row in enumerate(reader, 1):
            cursor.execute(
                """
INSERT INTO departments
(   name  ,   state  ,   dept_type  ,   url   ) VALUES
( %(name)s, %(state)s, %(dept_type)s, %(url)s ) ON CONFLICT DO NOTHING
                """,
                row,
            )
        print("Imported {:,} departments...".format(i))


def get_args():
    parser = argparse.ArgumentParser(description=__doc__)
    return vars(parser.parse_args())


def ingest_from_csvs():
    with psycopg2.connect(**DBAUTH) as conn:
        conn.cursor_factory = psycopg2.extras.RealDictCursor
        cursor = conn.cursor()
        cursor.execute("""DROP TABLE IF EXISTS departments""")
        cursor.execute("""CREATE TABLE departments (name text, state text, dept_type text, url text)""")
        cursor.execute("""CREATE UNIQUE INDEX ON departments (name, state)""")
        cursor.execute("""CREATE UNIQUE INDEX ON departments (state, name)""")
        for root, _, files in os.walk("data/departments/"):
            for ifile in files:
                import_one_state(cursor, os.path.join(root, ifile))
        conn.commit()

def main():
    """For each state ask wikipedia for a list of law enforcement agencies there and write those to DB."""
    get_args()
    start = time.time()
    while True:
        try:
            return ingest_from_csvs()
        except Exception as oops:
            if time.time() - start < 5:
                time.sleep(0.5)
            else:
                raise


if "__main__" == __name__:
    main()
