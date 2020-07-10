"""Get info about the given zipcode for the frontend."""
import json
import os
import string
import sys
import time
import traceback

import psycopg2
import psycopg2.extras
import requests

DBAUTH = {
    "dbname": "postgres",
    "password": "supersecret",
    "port": 5432,
    "user": "postgres",
    "host": "postgres",  # the name of the docker container we want to talk to is postgres and it's linked to this one by that name
}


def get_gov_info_for_zip(zipcode):
    response = requests.get(
        "https://www.googleapis.com/civicinfo/v2/representatives",
        params={
            "address": zipcode,
            "includeOffices": True,
            "key": os.environ["GCE_API_KEY"],
        },
    )
    response.raise_for_status()
    return response.json()


class ZipInfoResource:
    def __init__(self):
        self.conn = None
        self._zip_to_info = {}
        self._reinit()

        # populate _zip_to_info
        cursor = self.conn.cursor()
        cursor.execute("SELECT zipcode, city, state_abbr FROM geodata")
        for row in cursor:
            row = {k.lower(): v.lower() for k, v in dict(row).items()}
            zipcode = row.pop("zipcode")
            self._zip_to_info[zipcode] = row
        self._state_abbr_to_full = {
            "AL": "Alabama",
            "AK": "Alaska",
            "AS": "American Samoa",
            "AZ": "Arizona",
            "AR": "Arkansas",
            "CA": "California",
            "CO": "Colorado",
            "CT": "Connecticut",
            "DE": "Delaware",
            "DC": "District of Columbia",
            "FL": "Florida",
            "GA": "Georgia",
            "GU": "Guam",
            "HI": "Hawaii",
            "ID": "Idaho",
            "IL": "Illinois",
            "IN": "Indiana",
            "IA": "Iowa",
            "KS": "Kansas",
            "KY": "Kentucky",
            "LA": "Louisiana",
            "ME": "Maine",
            "MD": "Maryland",
            "MA": "Massachusetts",
            "MI": "Michigan",
            "MN": "Minnesota",
            "MS": "Mississippi",
            "MO": "Missouri",
            "MT": "Montana",
            "NE": "Nebraska",
            "NV": "Nevada",
            "NH": "New Hampshire",
            "NJ": "New Jersey",
            "NM": "New Mexico",
            "NY": "New York",
            "NC": "North Carolina",
            "ND": "North Dakota",
            "MP": "Northern Mariana Islands",
            "OH": "Ohio",
            "OK": "Oklahoma",
            "OR": "Oregon",
            "PA": "Pennsylvania",
            "PR": "Puerto Rico",
            "RI": "Rhode Island",
            "SC": "South Carolina",
            "SD": "South Dakota",
            "TN": "Tennessee",
            "TX": "Texas",
            "UT": "Utah",
            "VT": "Vermont",
            "VI": "Virgin Islands",
            "VA": "Virginia",
            "WA": "Washington",
            "WV": "West Virginia",
            "WI": "Wisconsin",
            "WY": "Wyoming",
        }

    def _reinit(self):
        attempts = list(range(5))
        while attempts:
            attempts.pop()
            try:
                self.conn = psycopg2.connect(**DBAUTH)
                self.conn.autocommit = True  # everything we're doing is read only...
                self.conn.cursor_factory = psycopg2.extras.RealDictCursor
                return
            except Exception:
                if not attempts:
                    raise
                print(traceback.format_exc(), file=sys.stderr)
                time.sleep(0.1)

    def on_get(self, request, response, **kwargs):
        try:
            zipcode = kwargs["zipcode"]
        except KeyError:
            return
        if len(zipcode) != 5:
            return
        if set(zipcode) - set(string.digits):
            return
        if self.conn is None:
            self._reinit()

        zipcode = kwargs.get("zipcode", "00000")
        query_kwargs = {"zipcode": zipcode}

        info_from_zip = self._zip_to_info.get(
            zipcode, {"state_abbr": "XX", "city": "xxxxx"}
        )

        state_abbr = info_from_zip["state_abbr"]
        city = info_from_zip["city"]
        full_state = self._state_abbr_to_full.get(state_abbr.upper(), "xxxxx")
        gov_info_for_zip = get_gov_info_for_zip(zipcode)
        print(locals())

        with self.conn.cursor() as cursor:
            # get lawyer info
            cursor.execute(
                "SELECT * FROM lawyers_with_firms WHERE zipcode = %(zipcode)s",
                query_kwargs,
            )
            lawyer_info = cursor.fetchall()

            # get law enforcement info
            # state level
            cursor.execute(
                "SELECT name, state, url FROM departments WHERE dept_type ILIKE %(statepattern)s AND LOWER(state) = %(state)s",
                {"state": full_state.lower(), "statepattern": "%state%",},
            )
            state_level = cursor.fetchall()

            # non-state level (this feels bad and wrong)
            cursor.execute(
                " ".join(
                    """
                SELECT
                    name, state, url
                FROM
                    departments
                WHERE
                    NAME ILIKE %(city_name_pattern)s AND
                    dept_type NOT ILIKE %(statepattern)s AND
                    state = %(state)s
                """.split()
                ),
                {
                    "city_name_pattern": "%{}%".format(city.lower()),
                    "state": full_state.lower(),
                    "statepattern": "%state%",
                },
            )
            local_level = cursor.fetchall()
            law_enforcement_info = local_level + state_level

        res = {
            "government_resources": gov_info_for_zip["officials"],
            "law_enforcement_resources": law_enforcement_info,
            "legal_resources": lawyer_info,
        }
        response.body = json.dumps(res)
