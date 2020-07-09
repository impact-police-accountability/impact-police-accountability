import argparse  # for parsing passed parameters through terminal

import bjoern
import falcon
from resources.hello import HelloResource
from resources.zipinfo import ZipInfoResource

wsgi_app = api = application = falcon.API()

# -- Edit Here --
api.req_options.auto_parse_form_urlencoded = True
api.add_route("/hello", HelloResource())
api.add_route("/{zipcode}", ZipInfoResource())
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
