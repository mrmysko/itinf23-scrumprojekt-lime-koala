#!/usr/bin/env python3

# Server software which fetches api stats from docker SDK from a list of ips.

import requests
from flask import Flask

# Create a flask server
app = Flask(__name__)

# Open the file with ips and read it to a variable.
with open("hosts.txt") as f:
    ips = f.read().splitlines()


# Flask endpoint /stats, only allowing GET requests.
@app.route("/stats", methods=["GET"])
def get_api_stats():
    # Dict comprehension for creating "ip: api_stats" key-value pairs from ips.
    hosts = {ip: requests.get(f"http://{ip}:5000/stats").json() for ip in ips}

    return hosts


@app.route("/container/all", methods=["GET"])
def ct_stats_all():
    return requests.get(f"http://10.255.255.155:5000/container/all").json()


if __name__ == "__main__":
    # Run flask listening on all ports.
    app.run(host="0.0.0.0", debug=True)
