#!/usr/bin/env python3

# curl -x <method> -H <url> -d <POST data>

import docker
import docker.errors
from flask import Flask, request, jsonify

app = Flask(__name__)

client = docker.from_env()

# This only fetches containers at start, how to update on new containers without agent reboot?
ct_names = [x.name for x in client.containers.list(all=True)]
print(ct_names)


# API Info?
@app.route("/stats", methods=["GET"])
def get_items():
    items = client.api.info()
    return jsonify(items)


@app.route("/container/<name>", methods=["GET"])
def ct_stats(name):
    if name in ct_names:
        cont = client.containers.get(name)
        return jsonify(cont.stats(stream=False))
    else:
        return not_found(name)


# Change this to a POST
@app.route("/container/<name>/stop", methods=["GET"])
def ct_stop(name):
    if name in ct_names:
        cont = client.containers.get(name)
        try:
            cont.stop()
            return f"Stopping {name}.", 200
        except docker.errors.APIError:
            return f"Could not stop {name}", 500
    else:
        return not_found(name)


# Change this to a POST
@app.route("/container/<name>/start", methods=["GET"])
def ct_start(name):
    if name in ct_names:
        cont = client.containers.get(name)
        try:
            cont.start()
            return f"Starting {name}.", 200
        except docker.errors.APIError:
            return f"Could not start {name}.", 500
    else:
        return not_found(name)


def not_found(name):
    return f"{name} not found.", 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
