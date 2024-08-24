#!/usr/bin/env python3

# Make a curl request for testing:
# curl -x <method> <url> OPTIONAL: -H <header> -d <POST data>

import docker
from flask import Flask, request, jsonify

# Create a Flask app
app = Flask(__name__)

# Create a client for the local docker engine
client = docker.from_env()

# THOUGHT - This only fetches containers at start, how to update on new containers without agent reboot?
# Creates a list of all container names.
ct_names = [x.name for x in client.containers.list(all=True)]
print(ct_names)


# API Info?
@app.route("/stats", methods=["GET"])
def api_stats():
    items = client.api.info()
    return jsonify(items)


# THOUGHT - Getting all information is time consuming in a single thread, multithread?
@app.route("/container/all", methods=["GET"])
def ct_stats_all():
    ct_stats_list = [
        client.containers.get(name).stats(stream=False) for name in ct_names
    ]
    return jsonify(ct_stats_list)


@app.route("/container/<name>", methods=["GET"])
def ct_stats(name):
    # Look if the name exists and create it's container object.
    if name in ct_names:
        cont = client.containers.get(name)
        # Return a single snapshot of that containers stats, converted to json.
        return jsonify(cont.stats(stream=False))
    else:
        return not_found(name)


# THOUGHT - Change this to a POST
@app.route("/container/<name>/stop", methods=["GET"])
def ct_stop(name):
    # Look if the name exists and create it's container object.
    if name in ct_names:
        cont = client.containers.get(name)
        # Try to stop the container, return an error if not successful (APIerror raised).
        try:
            cont.stop()
            return f"Stopped {name}.", 200
        except docker.errors.APIError:
            return f"Could not stop {name}", 500
    else:
        return not_found(name)


# THOUGHT - Change this to a POST
@app.route("/container/<name>/start", methods=["GET"])
def ct_start(name):
    # Look if the name exists and create it's container object.
    if name in ct_names:
        cont = client.containers.get(name)
        # Try to start the container, return an error if not successful (APIerror raised).
        try:
            cont.start()
            return f"Starting {name}.", 200
        except docker.errors.APIError:
            return f"Could not start {name}.", 500
    else:
        return not_found(name)


# If the container doesnt exist, return a message and 404.
def not_found(name):
    return f"{name} not found.", 404


if __name__ == "__main__":
    # Start the webserver listening on all interfaces.
    app.run(host="0.0.0.0", debug=True)
