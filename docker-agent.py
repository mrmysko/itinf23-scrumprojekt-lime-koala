#!/usr/bin/env python3

# TODO - Stream stats instead of snapshot.
# TODO - Error handling - crashing if a container is stopped
# TODO - SLOW! Gathering stats is slow even with only two containers.
# TODO - Container status not updating on fetch. Set on container object creation?
# Go back to getting container objects on request.

# curl -x <method> <url> -d <POST data>

import docker
from flask import Flask, request, jsonify
import pprint

app = Flask(__name__)

client = docker.from_env()

# This only fetches containers at start, how to update on new containers without agent reboot?
# Creates a dict with <ct_name>: <ct_object> key-value pairs.

containers = {x.name: x for x in client.containers.list(all=True)}
images = client.images.list()
formatted_images = [
    str(item).replace("<Image: '", "").replace("'>", "") for item in images
]
# formatted_list = [image.name for image in images]
# print(images)
# print(containers)
# print("1", formatted_images[0])
# print("2", dir(images[1]))
# print("3", dir(formatted_images[0]))


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

    # Get hostname
    hostname = client.api.info().get("Name")

    # Create nested dict with hostname as top value
    all_stats = dict()
    all_stats[hostname] = dict()

    # Add container stats from global containers dict.
    all_stats[hostname].update(
        {
            key: value
            for container in containers.values()
            for key, value in pick_stats(container).items()
        }
    )

    return jsonify(all_stats)


@app.route("/container/<name>", methods=["GET"])
def ct_stats(name):
    """
    API endpoint for fetching container stats.
    """
    # Look if container exists.
    if name in containers.keys():
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
    if name in containers.keys():
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
    if name in containers.keys():
        cont = client.containers.get(name)
        # Try to start the container, return an error if not successful (APIerror raised).
        try:
            cont.start()
            return f"Starting {name}.", 200
        except docker.errors.APIError:
            return f"Could not start {name}.", 500
    else:
        return not_found(name)


# Change this to a POST
@app.route("/image/run", methods=["GET", "POST"])
def img_run():
    """
    Run a container from image by name
    """
    if request.method == "POST":
        try:
            data = request.get_json(force=True)
            image_name = data.get("image")
            if not image_name:
                return "Image is required", 400
            try:
                client.containers.run(image_name)
                return f"Spinning up {image_name}.", 200
            except docker.errors.APIError:
                return f"Could not start {image_name}.", 500
        except Exception as e:
            return f"Failed to decode JSON object: {str(e)}", 400

    else:
        return "Method not allowed", 405


@app.route("/image/all", methods=["GET"])
def img_list():
    """
    Lists all current images on host
    """
    # Look if the name exists and create it's container object.
    #    image_list = client.images.list()
    #    print(image_list)
    return formatted_images


def not_found(name):
    """
    Return a not found message and a 404 status code.
    """
    return f"{name} not found.", 404


def pick_stats(ct):
    """
    Picks out relevant container stats and formats them in a nested dict.
    """

    # Save container stats
    stats = ct.stats(stream=False)
    # stats = next(ct.stats(decode=True))

    # pprint.pprint(stats)

    # Nested dict with container name as the top.
    ct_stats = dict()
    ct_stats[ct.name] = dict()

    # Status
    ct_stats[ct.name]["status"] = ct.status

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
    ct_stats[ct.name]["cpu_percent"] = round(ct_cpu / system_cpu * cores * 100, 2)

    # ___________________________________
    # Format memory usage as a percentage.
    mem_stats = stats["memory_stats"]

    # Memory usage / Memory limit * 100
    # Docker stats shows 0.01%, this shows 0.03%...hmmmm
    ct_stats[ct.name]["mem_percent"] = round(
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
