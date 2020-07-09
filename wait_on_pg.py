"""Just give postgres a few seconds to wake up after doing docker-compose up."""
import argparse
import time

import psycopg2

from config import DBAUTH


def wait_on_pg():
    start = time.time()
    while True:
        try:
            with psycopg2.connect(**DBAUTH) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                have_waited = time.time() - start
                print("Got connection after {:.2f}s...".format(have_waited))
                return
        except Exception as oops:
            have_waited = time.time() - start
            if have_waited < 5:
                print("Have waited {:.2f}s...".format(have_waited))
                time.sleep(0.5)
            else:
                raise


def get_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()


def main():
    get_args()
    wait_on_pg()


if "__main__" == __name__:
    main()
