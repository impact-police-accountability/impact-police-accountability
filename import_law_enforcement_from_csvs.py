"""Import law enforcement agency information from CSVs in the data dir."""
import argparse
import csv
import os
import time

import psycopg2
import psycopg2.extras

from config import DBAUTH
from wait_on_pg import wait_on_pg


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

def collapse_federal_agencies(cursor):
    # TODO: this ends up blowing away the URL attached to any of these in the state pages
    print("Collapsing federal agencies...")
    query = """
    WITH federal_agencies AS (
        DELETE FROM departments WHERE dept_type ILIKE '%federal%' RETURNING name
    ),
    unique_federal_agencies AS (
        SELECT name FROM federal_agencies GROUP BY name ORDER BY name
    )
    INSERT INTO
        departments (name, dept_type)
    SELECT
        name, 'federal'
    FROM
        unique_federal_agencies
    """
    cursor.execute(query)

def remove_old_agencies(cursor):
    print("Removing defunct/disbanded agencies...")
    for badpattern in ("%defunct%", "%disband%"):
        cursor.execute("DELETE FROM departments WHERE dept_type ILIKE %(badpattern)s", {"badpattern": badpattern})

def ingest_from_csvs():
    with psycopg2.connect(**DBAUTH) as conn:
        conn.cursor_factory = psycopg2.extras.RealDictCursor
        cursor = conn.cursor()
        cursor.execute("""DROP TABLE IF EXISTS departments""")
        cursor.execute(
            """CREATE TABLE departments (name text, state text, dept_type text, url text)"""
        )
        cursor.execute("""CREATE UNIQUE INDEX ON departments (name, state)""")
        cursor.execute("""CREATE UNIQUE INDEX ON departments (state, name)""")
        for root, _, files in os.walk("data/departments/"):
            for ifile in files:
                import_one_state(cursor, os.path.join(root, ifile))

        remove_old_agencies(cursor)
        collapse_federal_agencies(cursor)

        conn.commit()


def main():
    """For each state ask wikipedia for a list of law enforcement agencies there and write those to DB."""
    get_args()
    wait_on_pg()
    start = time.time()
    return ingest_from_csvs()


if "__main__" == __name__:
    main()
