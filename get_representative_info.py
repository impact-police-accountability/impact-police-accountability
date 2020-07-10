import argparse
import os
import json

import requests


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("zipcode")
    return vars(parser.parse_args())

def get_info_for_zip(zipcode):
    response = requests.get(
        "https://www.googleapis.com/civicinfo/v2/representatives",
        params={
            "address": zipcode,
            "includeOffices": True,
            "key": os.environ["GCE_API_KEY"],
        },
    )
    response.raise_for_status()
    return response.json()["officials"]


def main():
    args = get_args()
    print(
        json.dumps(get_info_for_zip(args["zipcode"]), indent=4, sort_keys=True)
    )


if "__main__" == __name__:
    main()
