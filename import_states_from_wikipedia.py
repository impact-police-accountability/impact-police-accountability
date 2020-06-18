import re

import psycopg2
from titlecase import titlecase
from unidecode import unidecode

from config import DBAUTH
from wiki import Wikipedia

# https://www.usacops.com/
# or try to ingest from here?


def get_depts_by_state(state):
    """For a single state, get the list of law enforcement agencies in that state (with a little bit of info about it)."""
    state = titlecase(state, small_first_last=False)
    raw = Wikipedia()["List of law enforcement agencies in {}".format(state)]
    parsed = {}
    current_category = None
    link_regex = re.compile(r"\[([^\[\]]*)\]")
    for row in raw.lower().split("\n"):
        if row.startswith("=="):
            current_category = row.strip("= ").lower()
            parsed[current_category] = set()
        elif current_category is not None:
            if "*" not in row:
                continue  # want just the listy things
            if "[" not in row:
                continue
            link_target = link_regex.search(row).groups()[0]
            printable_name = unidecode(link_target.split("|")[-1])
            if "http" in printable_name:
                printable_name = " ".join(printable_name.split()[1:])
            parsed[current_category].add(printable_name)
    parsed.pop("references", None)
    parsed.pop("see also", None)
    parsed.pop("defunct agencies", None)
    return parsed


def get_states():
    """Just return a list of the 50 states."""
    with open("states.txt") as states_fh:
        return sorted(r.strip() for r in states_fh)


def main():
    """For each state ask wikipedia for a list of law enforcement agencies there and write those to DB."""
    with psycopg2.connect(**DBAUTH) as conn:
        cursor = conn.cursor()
        for state in get_states():
            print(state)
            state_depts = get_depts_by_state(state)
            state = state.lower()
            while state_depts:
                dept_type, dept_list = state_depts.popitem()
                for name in sorted(dept_list):
                    print(name, dept_type, state)
                    cursor.execute(
                        """
INSERT INTO departments
(   name,     state,     dept_type   ) VALUES
( %(name)s, %(state)s, %(dept_type)s ) ON CONFLICT DO NOTHING""",
                        dict(locals()),
                    )
        conn.commit()


if "__main__" == __name__:
    main()
