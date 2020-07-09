"""Export lawyer data to the datadir."""
import argparse
import csv
import os

import psycopg2
import psycopg2.extras
import psycopg2.sql

from config import DBAUTH


def export_table(cursor, tablename):
    table_ident = psycopg2.sql.Identifier(tablename)
    query = psycopg2.sql.SQL("SELECT * FROM {} ORDER BY 1, 2").format(table_ident)
    cursor.execute(query)
    columns = [c.name for c in cursor.description]
    os.makedirs("data/{}".format(tablename), exist_ok=True)
    filename = "data/{tablename}/{tablename}.csv".format(tablename=tablename)
    with open(filename, "w") as fh:
        writer = csv.DictWriter(fh, columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(dict(x) for x in cursor)


def get_args():
    parser = argparse.ArgumentParser(description=__doc__)
    return vars(parser.parse_args())


def main():
    """Export lawyer data to the datadir."""
    get_args()
    with psycopg2.connect(**DBAUTH) as conn:
        conn.cursor_factory = psycopg2.extras.RealDictCursor
        cursor = conn.cursor()
        export_table(cursor, "lawyers")
        export_table(cursor, "law_firms")


if "__main__" == __name__:
    main()
