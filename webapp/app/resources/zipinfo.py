"""Get info about the given zipcode for the frontend."""
import json
import sys
import time
import traceback

import psycopg2
import psycopg2.extras

DBAUTH = {
    "dbname": "postgres",
    "password": "supersecret",
    "port": 5432,
    "user": "postgres",
    "host": "postgres",  # the name of the docker container we want to talk to is postgres and it's linked to this one by that name
}


class ZipInfoResource:
    def __init__(self):
        self.conn = None

    def _reinit(self):
        attempts = list(range(5))
        while attempts:
            attempts.pop()
            try:
                self.conn = psycopg2.connect(**DBAUTH)
                self.conn.cursor_factory = psycopg2.extras.RealDictCursor
                return
            except Exception:
                if not attempts:
                    raise
                print(traceback.format_exc(), file=sys.stderr)
                time.sleep(0.1)

    def on_get(self, request, response, **kwargs):
        if self.conn is None:
            self._reinit()

        query_kwargs = {"zipcode": kwargs.get("zipcode", "00000")}
        full_state = "massachusetts"
        city = "Boston"
        with self.conn.cursor() as cursor:
            # get lawyer info
            cursor.execute(
                "SELECT * FROM lawyers_with_firms WHERE zipcode = %(zipcode)s",
                query_kwargs,
            )
            lawyer_info = cursor.fetchall()

            # get government info
            cursor.execute("SELECT 'the best agency' AS name UNION ALL SELECT 'the second best agency'")
            gov_info = cursor.fetchall()

            # get law enforcement info
            # state level
            cursor.execute(
                "SELECT * FROM departments WHERE dept_type ILIKE %(statepattern)s AND state = %(state)s",
                {
                    "state": full_state,
                    "statepattern": "%state%",
                }
            )
            state_level = cursor.fetchall()

            # non-state level (this feels bad and wrong)
            cursor.execute(
                """SELECT * FROM departments WHERE NAME ILIKE %(city_name_pattern)s AND dept_type NOT ILIKE %(statepattern)s AND state = %(state)s""",
                {
                    "city_name_pattern": "%{}%".format(city.lower()),
                    "state": full_state,
                    "statepattern": "%state%",
                }
            )
            local_level = cursor.fetchall()
            law_enforcement_info = local_level + state_level


        res = {
            "government_resources": gov_info,
            "law_enforcement_resources": law_enforcement_info,
            "legal_resources": lawyer_info,
        }
        response.body = json.dumps(res)
