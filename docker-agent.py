#!/usr/bin/env python3

# TODO - Stream stats instead of snapshot.
# TODO - Move away from global variables, its lazy.

# curl -x <method> <url> -d <POST data>

import docker
from flask import Flask, request, jsonify
from concurrent.futures import ThreadPoolExecutor
import threading
import time

# Create a flask app
app = Flask(__name__)

client = docker.from_env()
containers = [x.name for x in client.containers.list(all=True)]


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
    API endpoint to serve all container stats.
    """

    return jsonify(host)


@app.route("/container/<name>", methods=["GET"])
def ct_stats(name):
    """
    API endpoint for fetching container stats.
    """

    # Look if container exists.
    if name in containers:
        # Return a single snapshot of that containers stats, converted to json.
        return jsonify(select_stats(containers[name]))
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


@app.route("/container/all/prune", methods=["Get"])
def prune():
    # a api endpoint for pruning containers.

    # this will prune the containers
    client.containers.prune()

    return "containers have been pruned"


@app.route("/image/run", methods=["POST"])
def img_run():
    """
    Run a container from image by name
    """
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


@app.route("/image/all", methods=["GET"])
def img_list():
    """
    Lists all current images on host
    """

    return formatted_images


def not_found(name):
    """
    Return a not found message and a 404 status code.
    """
    return f"{name} not found.", 404


def select_stats(ct) -> dict:
    """
    Picks out relevant container stats and formats them in a nested dict.
    """

    # Save container stats
    ct_obj = client.containers.get(ct)
    stats = ct_obj.stats(stream=False)

    # Nested dict with container name as the top.
    ct_stats = dict()
    ct_stats[ct] = dict()

    # Status
    ct_stats[ct]["status"] = ct_obj.status

    # Check if container status NOT running, just return status then.
    if ct_obj.status != "running":
        return ct_stats

    # Stream doesnt include precpu data
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


def background_updates():
    """
    Update available containers, stats and images.
    """
    # Makes the containers with stats and formatted images available in a global context.
    global containers
    global formatted_images

    while True:
        # Creates a list with container names.
        containers = [x.name for x in client.containers.list(all=True)]

        # Create a formatted list with image names.
        images = client.images.list()
        formatted_images = [
            str(item).replace("<Image: '", "").replace("'>", "") for item in images
        ]
        # Update every 5 seconds
        time.sleep(5)


def background_ct_stats():
    """
    Update container stats in the background.
    """
    # Expose host globally.
    global host

    # Create a dict structure for container data.
    host = {"hostname": client.api.info().get("Name"), "containers": {}}

    while True:
        # Multithread stats collection.
        with ThreadPoolExecutor() as executor:
            fetched_stats = executor.map(select_stats, containers, timeout=5)

        # Update dict from every fetched container stat.
        for value in fetched_stats:
            host["containers"].update(value)


if __name__ == "__main__":
    # Creates a thread that runs background tasks.
    threading.Thread(target=background_updates, daemon=True).start()
    # Create a thread that updates container stats sin the background.
    threading.Thread(target=background_ct_stats, daemon=True).start()
    # Start the webserver listening on all interfaces.
    app.run(host="0.0.0.0", debug=True)
