import csv
import os
import re

import psycopg2
import psycopg2.extras

from config import DBAUTH


def import_one_state(cursor, filepath):
    with open(filepath) as fh:
        reader = csv.DictReader(fh)
        # construct the insert statement...
        for row in reader:
            cursor.execute(
                """
INSERT INTO depts_copy
(   name  ,   state  ,   dept_type  ,   url   ) VALUES
( %(name)s, %(state)s, %(dept_type)s, %(url)s ) ON CONFLICT DO NOTHING
                """,
                row,
            )
        return


def main():
    """For each state ask wikipedia for a list of law enforcement agencies there and write those to DB."""
    with psycopg2.connect(**DBAUTH) as conn:
        conn.cursor_factory = psycopg2.extras.RealDictCursor
        cursor = conn.cursor()
        for root, _, files in os.walk("data"):
            for ifile in files:
                import_one_state(cursor, os.path.join(root, ifile))
        conn.commit()


if "__main__" == __name__:
    main()
