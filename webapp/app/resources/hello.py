import json


class HelloResource:
    def on_get(self, request, response):
        print("hello world")
        response.body = json.dumps("hello world")
