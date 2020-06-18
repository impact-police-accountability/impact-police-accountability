import argparse  # for parsing passed parameters through terminal
import json
from ipaddress import ip_address

import bjoern
import falcon

wsgi_app = api = application = falcon.API()

# -- Edit Here --
class IndexResource:
    def on_get(self, request, response):
        print("hello world")
        response.body = json.dumps("hello world")


api.req_options.auto_parse_form_urlencoded = True
api.add_route("/foo", IndexResource())  # attach resources to API
# -- End of Edit --


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    return vars(parser.parse_args())


def main():
    args = get_args()
    print("Starting webserver on {}".format(args["port"]))
    bjoern.run(wsgi_app, "0.0.0.0", args["port"])


if __name__ == "__main__":
    main()
