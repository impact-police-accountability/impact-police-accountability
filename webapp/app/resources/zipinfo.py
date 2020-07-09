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

        with self.conn.cursor() as cursor:
            cursor.execute("SELECT * FROM lawyers_with_firms LIMIT 10")
            res = cursor.fetchall()
        response.body = json.dumps(res)
