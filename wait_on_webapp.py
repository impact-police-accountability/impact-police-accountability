"""Just give postgres a few seconds to wake up after doing docker-compose up."""
import argparse
import os
import time

import requests


def wait_on_webapp():
    start = time.time()
    url = "http://localhost:{}/foo".format(os.environ["IPA_PORT_WEBAPP"])
    while True:
        try:
            response = requests.get(url)
            response.raise_for_status()
            return
        except Exception as oops:
            have_waited = time.time() - start
            if have_waited < 5:
                print("Have waited {:.2f}s for webapp to start...".format(have_waited))
                time.sleep(0.1)
            else:
                raise


def get_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()


def main():
    get_args()
    wait_on_webapp()


if "__main__" == __name__:
    main()
