import psycopg2
import psycopg2.extras

from config import DBAUTH
from google_helper import google_search

# https://cse.google.com/cse/setup/basic?cx=005745791240568855764:8kbdzx8804g


def main():
    with psycopg2.connect(**DBAUTH) as conn:
        conn.cursor_factory = psycopg2.extras.RealDictCursor
        read_cursor = conn.cursor()
        write_cursor = conn.cursor()
        read_cursor.execute(
            "SELECT * FROM departments WHERE url IS NULL ORDER BY HASHTEXT(name)"
        )
        for row in read_cursor:
            row = dict(row)
            query = row["name"] + " " + row["state"]
            try:
                search_res = google_search(query)
            except KeyError:
                print("Missed on {}...".format(query))
                continue
            row["url"] = search_res[0]["link"]
            write_cursor.execute(
                "UPDATE departments SET url = %(url)s WHERE name = %(name)s AND state = %(state)s",
                row,
            )
            conn.commit()  # commit after each update
        conn.commit()
    # print(json.dumps(google_search("wheatland police department wyoming"), indent=4, sort_keys=True))


if "__main__" == __name__:
    main()
