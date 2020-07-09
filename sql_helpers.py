import csv

import psycopg2


def import_table(cursor, tablename, filepath, delimiter=","):
    print("Importing {} to {}...".format(filepath, tablename))
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
    with open(filepath) as fh:
        reader = csv.DictReader(fh, delimiter=delimiter)
        for row in reader:
            cursor.execute(stmt_as_sql, row)
