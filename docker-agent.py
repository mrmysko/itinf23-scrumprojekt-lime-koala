#!/usr/bin/env python3

# TODO - Stream stats instead of snapshot.
# TODO - Error handling - crashing if a container is stopped
# TODO - SLOW! Gathering stats is slow even with only two containers.

# curl -x <method> <url> -d <POST data>

import docker
from flask import Flask, request, jsonify

app = Flask(__name__)

client = docker.from_env()

# This only fetches containers at start, how to update on new containers without agent reboot?
# Creates a list with container names.
containers = [x.name for x in client.containers.list(all=True)]


# API Info?
@app.route("/stats", methods=["GET"])
def client_api_stats():
    """
    API endpoint for getting docker api stats
    """
    items = client.api.info()
    return jsonify(items)


# Getting all information is time consuming in a single thread, multithreading?
@app.route("/container/all", methods=["GET"])
def ct_stats_all():
    """
    API endpoint for getting stats from all containers.
    """

    # Create a dict for all stats
    all_stats = dict()
    # Get hostname
    all_stats["hostname"] = client.api.info().get("Name")

    # Add container stats to containers key.
    all_stats["containers"] = {
        key: value
        for container in containers
        for key, value in pick_stats(container).items()
    }

    return jsonify(all_stats)


@app.route("/container/<name>", methods=["GET"])
def ct_stats(name):
    """
    API endpoint for fetching container stats.
    """
    # Look if container exists.
    if name in containers:
        # Return a single snapshot of that containers stats, converted to json.
        return jsonify(pick_stats(containers[name]))
    else:
        return not_found(name)


# Change this to a POST
@app.route("/container/<name>/stop", methods=["GET"])
def ct_stop(name):
    """
    Stop a container by name
    """
    # Look if the name exists and create it's container object.
    if name in containers:
        cont = client.containers.get(name)
        # Try to start the container, return an error if not successful (APIerror raised).
        try:
            cont.stop()
            return f"Stopped {name}.", 200
        except docker.errors.APIError:
            return f"Could not stop {name}", 500
    else:
        return not_found(name)


# Change this to a POST
@app.route("/container/<name>/start", methods=["GET"])
def ct_start(name):
    """
    Start a container by name
    """
    # Look if the name exists and create it's container object.
    if name in containers:
        cont = client.containers.get(name)
        # Try to start the container, return an error if not successful (APIerror raised).
        try:
            cont.start()
            return f"Starting {name}.", 200
        except docker.errors.APIError:
            return f"Could not start {name}.", 500
    else:
        return not_found(name)


def not_found(name):
    """
    Return a not found message and a 404 status code.
    """
    return f"{name} not found.", 404


def pick_stats(ct) -> dict:
    """
    Picks out relevant container stats and formats them in a nested dict.
    """

    # Save container stats
    ct_obj = client.containers.get(ct)
    stats = ct_obj.stats(stream=False)
    # stats = next(ct.stats(decode=True))

    # Nested dict with container name as the top.
    ct_stats = dict()
    ct_stats[ct] = dict()

    # Status
    ct_stats[ct]["status"] = ct_obj.status

    # If container status is exited, then move on.
    if ct.status == "exited":
        return 

    # _________________________________
    # Format CPU usage as a percentage.
    cpu_stats = stats["cpu_stats"]
    precpu_stats = stats["precpu_stats"]

    # Container CPU
    ct_cpu = (
        cpu_stats["cpu_usage"]["total_usage"] - precpu_stats["cpu_usage"]["total_usage"]
    )
    # System CPU
    system_cpu = cpu_stats["system_cpu_usage"] - precpu_stats["system_cpu_usage"]
    # Number of cores
    cores = cpu_stats["online_cpus"]

    # Container CPU / System CPU * Number of cores * 100
    ct_stats[ct]["cpu_percent"] = round(ct_cpu / system_cpu * cores * 100, 2)

    # ___________________________________
    # Format memory usage as a percentage.
    mem_stats = stats["memory_stats"]

    # Memory usage / Memory limit * 100
    # Docker stats shows 0.01%, this shows 0.03%...hmmmm
    ct_stats[ct]["mem_percent"] = round(
        mem_stats["usage"] / mem_stats["limit"] * 100, 2
    )

    return ct_stats


if __name__ == "__main__":
    # Start the webserver listening on all interfaces.
    app.run(host="0.0.0.0", debug=True)

# Stream stats on a 5 sec timer
# while True:
#   pprint.pprint(next(ct.stats(decode=True)))
#   time.sleep(5)