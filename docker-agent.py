#!/usr/bin/env python3

import docker
from flask import Flask, request, jsonify

app = Flask(__name__)

client = docker.from_env()


@app.route("/stats", methods=["GET"])
def get_items():
    items = client.api.info()
    return jsonify(items)


@app.route("/container/<name>", methods=["GET", "POST"])
def process_command(name):
    for cont in client.containers.list():
        if cont.name == name:
            return jsonify(cont.stats(stream=False))


def ct_stats(name):
    pass


def ct_stop(name):
    pass


def ct_start(name):
    pass


if __name__ == "__main__":
    app.run(host="0.0.0.0")
