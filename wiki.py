import json

import requests


class Wikipedia:
    def __init__(self):
        self.endpoint = "https://en.wikipedia.org/w/api.php"

    def __getitem__(
        self,
        titles="Competitive Advantage",
        format="json",
        action="query",
        prop="revisions",
        rvprop="content",
        rvslots="*",
    ):
        params = dict(locals())
        params = {
            k: params.get(k)
            for k in ["format", "action", "titles", "prop", "rvprop", "rvslots"]
        }
        params["titles"] = "_".join(titles.split())
        response = requests.get(self.endpoint, params=params)
        try:
            return response.json()["query"]["pages"].popitem()[1]["revisions"][0][
                "slots"
            ]["main"]["*"]
        except KeyError:
            print(response.url)
            print(json.dumps(response.json(), indent=4, sort_keys=True))
            raise
