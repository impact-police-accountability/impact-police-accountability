"""
Get info about lawyers and law firms prioritizing high population zipcodes, saving the data to S3.
"""
import argparse
import csv
import datetime
import json
import time
import traceback

import boto3
import bs4
import cloudscraper
import requests

global_session = cloudscraper.CloudScraper()
global_session.headers.update(
    {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:71.0) Gecko/20100101 Firefox/71.0"
    }
)


def get_lawyers_for_zipcode(zipcode):
    """Actually make the http request to get civil rights lawyers for a zipcode..., parse the data out of the html."""
    # TODO: cache the daylights out of this... because it's pretty gray-hat
    time.sleep(3)
    print(
        "Getting lawyers for {} @ {:%H:%M:%S}...".format(
            zipcode, datetime.datetime.now()
        )
    )
    response = global_session.get(
        "https://www.avvo.com/search/lawyer_search",
        params={"q": "civil rights", "loc": zipcode,},
    )
    try:
        response.raise_for_status()
    except:
        print(response.content)
        raise
    soup = bs4.BeautifulSoup(response.content, features="lxml")
    lawyers_for_zip = []
    for scripttag in soup.find_all("script", attrs={"type": "application/ld+json"}):
        parsed = json.loads(" ".join(scripttag.contents))
        parsed.pop("@context", None)
        lawyers_for_zip.append(parsed)
    return lawyers_for_zip


def record_lawyers_on_s3(zipcode):
    """Given a zipcode, fetch civil rights lawyers for that zipcode and dump the result on S3."""
    # TODO: probably fetch this data down from S3, process and save in DB
    bucket = boto3.resource("s3").Bucket("protect-the-people")
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
    emit = False
    with open("data/pop_by_zip_only.csv") as fh:
        reader = csv.DictReader(fh)
        for i, iline in enumerate(reader):
            if 3650 < i:
                # in the interest of being a good internet citizen don't do every zipcode...
                # would be nice to either find a better source of this data
                # of spread out the requests over the course of a few weeks
                break
            if "X" in iline["zipcode"]:
                # this is sad, but I don't know what to do
                continue
            if "70119" == iline["zipcode"]:
                emit = True
            if emit:
                yield iline["zipcode"]


def get_args():
    parser = argparse.ArgumentParser(description=__doc__)
    return parser.parse_args()


def main():
    get_args()
    for zipcode in gen_zipcodes():
        try:
            record_lawyers_on_s3(zipcode)
        except KeyboardInterrupt:
            break
        except:
            print(traceback.format_exc())


if "__main__" == __name__:
    main()
