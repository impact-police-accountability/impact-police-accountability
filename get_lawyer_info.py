"""
Get info about lawyers and law firms prioritizing high population zipcodes, saving the data to S3.
"""
import argparse
import csv
import datetime
import json
import time
import traceback

import bs4
import cloudscraper
import requests

from config import get_bucket

global_session = cloudscraper.CloudScraper()
requests_session = requests.Session()
for ithing in [global_session, requests_session]:
    ithing.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:71.0) Gecko/20100101 Firefox/71.0"
        }
    )

    ithing.cookies.update(
        {
            "avvo-login": "BAh7BkkiD3Nlc3Npb25faWQGOgZFVEkiKWUxMmExNDAxLTI5MGUtNDI5Mi04%0AYTJiLWZjODlhZWU2YTM0MgY7AFQ%3D%0A--3b72b4c744b47c204a65a601082274ac515569ab",
            "BIGipServeravvo-k8s-20080_POOL": "2731787530.28750.0000",
            "cf_clearance": "e29ec8b0430ba3a02fcc0937d42aba906a96133e-1594505610-0-1z805c028fz7aa4af08z63cedf24-250",
            "__cfduid": "df544bc41628cd87e2e394cc5a686cdcd1594165699",
            "maxLength": "1200",
            "_persistent_session_id": "BAh7BkkiD3Nlc3Npb25faWQGOgZFVEkiKTU5YWMwMzliLTNhYjMtNGRiNy1h%0AYWIyLWZkMDE2YmI1YTc2YwY7AFQ%3D%0A",
            "serp_search_prev_sig": "99914b932bd37a50b983c5e7c90ae93b",
            "_session_id": "f45fc839b19ef7ef91bfb65842b484e1",
        }
    )


def get_lawyers_for_zipcode(zipcode):
    """Actually make the http request to get civil rights lawyers for a zipcode..., parse the data out of the html."""
    # TODO: cache the daylights out of this... because it's pretty gray-hat
    time.sleep(61)
    print(
        "Getting lawyers for {} @ {:%H:%M:%S}...".format(
            zipcode, datetime.datetime.now()
        )
    )
    try:
        response = global_session.get(
            "https://www.avvo.com/search/lawyer_search",
            params={"q": "civil rights", "loc": zipcode,},
        )
        response.raise_for_status()
    except:
        response = requests_session.get(
            "https://www.avvo.com/search/lawyer_search",
            params={"q": "civil rights", "loc": zipcode,},
        )
        print("Failed getting {}...".format(response.url))
        print(traceback.format_exc())
        print(response.content)
        raise
    soup = bs4.BeautifulSoup(
        response.content, features="html.parser"
    )  # , features="lxml")
    lawyers_for_zip = []
    for scripttag in soup.find_all("script", attrs={"type": "application/ld+json"}):
        parsed = json.loads(" ".join(scripttag.contents))
        parsed.pop("@context", None)
        lawyers_for_zip.append(parsed)
    return lawyers_for_zip


def record_lawyers_on_s3(zipcode):
    """Given a zipcode, fetch civil rights lawyers for that zipcode and dump the result on S3."""
    # TODO: probably fetch this data down from S3, process and save in DB
    bucket = get_bucket()
    keyname = "lawyers/{}.json".format(zipcode)
    keyobj = bucket.Object(keyname)
    try:
        keyobj.load()
        return  # already exists, do not overwrite?
    except:
        pass
    lawyers = get_lawyers_for_zipcode(zipcode)
    keyobj.put(Body=json.dumps(lawyers, indent=4, sort_keys=True))


def gen_zipcodes():
    """Generate a sequence of zipcodes, from highest to lowest population, truncated after 3650 (~50% of us population)."""
    bucket = get_bucket()
    done = set()
    for obj in bucket.objects.filter(Prefix="lawyers/"):
        done.add(obj.key.split("/")[-1].split(".")[0])
    with open("data/pop_by_zip_only.csv") as fh:
        reader = csv.DictReader(fh)
        for i, iline in enumerate(reader):
            if i < len(done):
                continue
            if iline["zipcode"] in done:
                continue
            # in the interest of being a good internet citizen don't do every zipcode...
            # would be nice to either find a better source of this data
            # of spread out the requests over the course of a few weeks
            if "X" in iline["zipcode"]:
                # this is sad, but I don't know what to do
                continue
            yield iline["zipcode"]


def get_args():
    parser = argparse.ArgumentParser(description=__doc__)
    return parser.parse_args()


def main():
    get_args()
    for idx, zipcode in enumerate(gen_zipcodes(), 1):
        print(
            "Doing the {:,}th zipcode @ {:%H:%M:%S}...".format(
                idx, datetime.datetime.now()
            )
        )
        try:
            record_lawyers_on_s3(zipcode)
        except KeyboardInterrupt:
            break
        except:
            print(traceback.format_exc())


if "__main__" == __name__:
    main()
