"""docstring?"""
import hashlib
import json
import os
import time

import requests

from config import get_bucket


def get_google_search():
    bucket = get_bucket()
    gce_api_key = os.environ["GCE_API_KEY"]

    def md5(istr):
        return hashlib.sha256(istr.encode("utf-8")).hexdigest()

    def google_search_inner(query):
        md5_of_query = md5(query)
        keyname = "{:.2}/{}".format(md5_of_query, md5_of_query)
        keyobj = bucket.Object(keyname)
        try:
            raw_ans = json.load(keyobj.get()["Body"])
        except:
            raw_ans = None
        if raw_ans is None:
            # get approx 1 search per 8 seconds
            time.sleep(9)
            params = {
                "cx": "005745791240568855764:8kbdzx8804g",
                "key": gce_api_key,
                "q": query,
            }
            response = requests.get(
                "https://customsearch.googleapis.com/customsearch/v1", params=params
            )
            try:
                raw_ans = response.json()["items"]
            except KeyError:
                print(response.json())
                raise
            keyobj.put(Body=json.dumps(raw_ans, indent=4, sort_keys=True))
        return raw_ans

    return google_search_inner


google_search = get_google_search()
