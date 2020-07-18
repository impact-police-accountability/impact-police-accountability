import csv
import os

import psycopg2
import psycopg2.extras

from config import DBAUTH


def export_one_state(cursor, state):
    cursor.execute(
        "SELECT * FROM departments WHERE state IS NOT DISTINCT FROM %(state)s ORDER by 1, 2, 3",
        {"state": state},
    )
    cols = [c.name for c in cursor.description]
    # make a csv with the name of the state?
    tablename = "departments"
    os.makedirs("data/{}".format(tablename), exist_ok=True)
    if state:
        outpath = "data/{}/{}.csv".format(tablename, "_".join(state.split()))
    else:
        outpath = "data/{}/federal.csv".format(tablename)

    with open(outpath, "w") as outfile:
        writer = csv.DictWriter(outfile, cols, lineterminator="\n")
        writer.writeheader()
        writer.writerows(dict(x) for x in cursor)


def main():
    """For each state ask wikipedia for a list of law enforcement agencies there and write those to DB."""
    with psycopg2.connect(**DBAUTH) as conn:
        conn.cursor_factory = psycopg2.extras.RealDictCursor
        cursor = conn.cursor()
        cursor.execute("SELECT state FROM departments GROUP BY 1 ORDER BY 1")
        for state in [r["state"] for r in cursor]:
            export_one_state(cursor, state)
        export_one_state(cursor, None)


if "__main__" == __name__:
    main()
