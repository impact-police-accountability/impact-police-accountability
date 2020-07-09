"""Fetch lawyer data from S3 and pack it into a DB, probably then export to """

import json
import time

import psycopg2
import psycopg2.extras

from config import DBAUTH, get_bucket

"""
postgres=# \d+ lawyers
                                       Table "public.lawyers"
       Column       | Type | Collation | Nullable | Default | Storage  | Stats target | Description
--------------------+------+-----------+----------+---------+----------+--------------+-------------
 lawyer_name        | text |           |          |         | extended |              |
 law_firm_phone_num | text |           |          |         | extended |              |
Indexes:
    "lawyers_grain" UNIQUE, btree (lawyer_name, law_firm_phone_num)
Foreign-key constraints:
    "lawyers_law_firm_phone_num_fkey" FOREIGN KEY (law_firm_phone_num) REFERENCES law_firms(phone_number)
Access method: heap

postgres=# \d+ law_firms
                                    Table "public.law_firms"
     Column     | Type | Collation | Nullable | Default | Storage  | Stats target | Description
----------------+------+-----------+----------+---------+----------+--------------+-------------
 law_firm_name  | text |           |          |         | extended |              |
 phone_number   | text |           |          |         | extended |              |
 street_address | text |           |          |         | extended |              |
 city           | text |           |          |         | extended |              |
 state          | text |           |          |         | extended |              |
 zipcode        | text |           |          |         | extended |              |
Indexes:
    "law_firm_grain" UNIQUE, btree (phone_number)
Referenced by:
    TABLE "lawyers" CONSTRAINT "lawyers_law_firm_phone_num_fkey" FOREIGN KEY (law_firm_phone_num) REFERENCES law_firms(phone_number)
Access method: heap
"""


def get_args():
    parser = argparse.ArgumentParser(description=__doc__)
    return vars(parser.parse_args())


def import_one_key(cursor, key):
    lawyer_rows = json.load(key.get()["Body"])
    # print(json.dumps(lawyer_rows, indent=4, sort_keys=True))
    for ilawyer in lawyer_rows:
        try:
            worksfor = ilawyer["worksFor"]
        except:
            print(json.dumps(ilawyer, indent=4, sort_keys=True))
            continue
        address = worksfor["address"]
        # add law firm
        cursor.execute(
            """INSERT INTO law_firms
            (   law_firm_name  ,   phone_number  ,   street_address  ,   city  ,   state  ,   zipcode   ) VALUES
            ( %(law_firm_name)s, %(phone_number)s, %(street_address)s, %(city)s, %(state)s, %(zipcode)s ) ON CONFLICT DO NOTHING""",
            {
                "city": address["addressLocality"],
                "law_firm_name": worksfor["name"],
                "phone_number": worksfor["telephone"],
                "state": address["addressRegion"],
                "street_address": address["streetAddress"],
                "zipcode": address["postalCode"],
            },
        )

        # add lawyer
        cursor.execute(
            """INSERT INTO lawyers
            (   lawyer_name  ,   law_firm_phone_num   ) VALUES
            ( %(lawyer_name)s, %(law_firm)s ) ON CONFLICT DO NOTHING""",
            {"lawyer_name": ilawyer["name"], "law_firm": worksfor["telephone"],},
        )


def ensure_schema(conn):
    """Setup the schema for lawyering."""
    cursor = conn.cursor()

    if True:
        cursor.execute("""DROP TABLE IF EXISTS lawyers CASCADE""")
        cursor.execute("""DROP TABLE IF EXISTS law_firms CASCADE""")

    # law firms...
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS law_firms (law_firm_name text, phone_number text, street_address text, city text, state text, zipcode text)"""
    )  # what about the uniqueness of these...
    cursor.execute("""CREATE UNIQUE INDEX law_firm_grain ON law_firms (phone_number)""")

    # lawyers...
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS lawyers (lawyer_name text, law_firm_phone_num text REFERENCES law_firms (phone_number) )"""
    )  # is it the case that each lawyer lawfirm combination is unique?...
    cursor.execute(
        """CREATE UNIQUE INDEX lawyers_grain ON lawyers (lawyer_name, law_firm_phone_num)"""
    )

    # create a view lacing the two together...
    cursor.execute(
        """CREATE VIEW lawyers_with_firms AS SELECT * FROM lawyers LEFT JOIN law_firms ON lawyers.law_firm_phone_num = law_firms.phone_number"""
    )
    conn.commit()


def main():
    bucket = get_bucket()
    done = 0
    start_time = time.time()
    with psycopg2.connect(**DBAUTH) as conn:
        conn.cursor_factory = psycopg2.extras.RealDictCursor
        ensure_schema(conn)

        cursor = conn.cursor()
        for idx, key in enumerate(bucket.objects.filter(Prefix="lawyers/"), 1):
            if key.size < 3:
                continue
            done += 1
            print("Importing key {:,}...".format(idx))
            import_one_key(cursor, key)

        cursor.execute(
            "SELECT 'num_law_firms' AS key, SUM(1) AS value FROM law_firms UNION ALL SELECT 'num_lawyers', SUM(1) FROM lawyers"
        )
        info = {row["key"]: row["value"] for row in cursor}
        info["duration"] = time.time() - start_time
        print(
            "Imported {num_lawyers:,} lawyers in {num_law_firms:,} firms in {duration:.2f}s".format(
                **info
            )
        )
        conn.commit()


if "__main__" == __name__:
    main()
