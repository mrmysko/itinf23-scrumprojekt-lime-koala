#!/usr/bin/env python3

# Server software which manipulates remote hosts with agents listening.

import requests
import pprint
import os
from concurrent.futures import ThreadPoolExecutor

# Open the file with ips and read it to a variable.
with open("hosts.txt") as f:
    ips = f.read().splitlines()


def main():
    # Define "main menu" items.
    menu_items = {
        "1": "Print CT",
        "2": "Start CT",
        "3": "Stop CT",
        "4": "API status",
        "e": "Exit",
    }

    # Main menu loop.
    while True:
        clear_console()
        menu_print(menu_items)

        user_choice = input(": ")

        # Match user choice, no match reruns the loop.
        match user_choice:
            case "1":
                ct_stats_print(pool_requests(ips))
                input()
            case "2":
                ct_action(ips, "start")
            case "3":
                ct_action(ips, "stop")
            case "4":
                hosts_api_stats()
            case "e":
                break
            case _:
                pass


def clear_console():
    """
    Clears the console on both windows and unix systems.
    """

    command = "clear"
    if os.name == "nt":
        command = "cls"
    os.system(command)


def menu_print(menu_items={"b": "Go back."}):
    """
    Prints the menu.
    """

    print("|----------------|")
    print("| Docker Monitor |")
    print("|----------------|")

    for key, item in menu_items.items():
        print(f"{key}. {item.ljust(12)}", end="")
    print()


def ct_stats_request(ip):
    """
    Request container stats from hosts.
    """

    request = {ip: requests.get(f"http://{ip}:5000/container/all").json()}

    return request


def pool_requests(ips):
    """
    Multithread requests
    """

    with ThreadPoolExecutor() as executor:
        requested = executor.map(ct_stats_request, ips, timeout=10)

    hosts = {key: value for host in list(requested) for key, value in host.items()}

    # This re-enumerates on every new request atm.-
    enum_ct(hosts)

    return hosts


def ct_stats_print(hosts):
    """
    Prints container stats from all hosts.
    """

    # THIS CODE IS SUPER UGLY SHIEEEET
    for ip, value in hosts.items():
        print(f'{value["hostname"]} ({ip})')
        print(
            "ID".rjust(3),
            "Name".rjust(10),
            "Status".rjust(10),
            "% CPU".rjust(10),
            "% MEM".rjust(10),
        )
        for stat, stat_val in value["containers"].items():
            print(
                str(stat_val["id"]).rjust(3),
                stat.rjust(10),
                stat_val["status"].rjust(10),
                str(stat_val["cpu_percent"]).rjust(10),
                str(stat_val["mem_percent"]).rjust(10),
            )


def ct_action(ips, action):
    """
    Start a container by list id.
    """
    clear_console()
    menu_print()

    # Fetch container stats from hosts.
    hosts = pool_requests(ips)
    # Print them
    ct_stats_print(hosts)

    while True:
        id = input("ID: ")
        # Check if id is 0, a digit or something else.
        if id.lower() == "b":
            break
        elif id.isdigit():
            for ip, value in hosts.items():
                for ct_name, stats in value["containers"].items():
                    if stats["id"] == int(id):
                        if requests.get(
                            f"http://{ip}:5000/container/{ct_name}/{action}"
                        ):
                            print(f"{action} {ct_name}")
                        else:
                            print(f"Could not {action} {ct_name}")
                        input()
                        break
            else:
                pass


def hosts_api_stats():
    """
    Prints agent hosts api stats.
    """
    # Dict comprehension for creating "ip: api_stats" key-value pairs from ips.
    hosts = {ip: requests.get(f"http://{ip}:5000/stats").json() for ip in ips}

    pprint.pprint(hosts)
    input()


def enum_ct(hosts):
    """
    Enumerate containers so that they are accessible by a number for start/stop
    """

    id = 1
    for value in hosts.values():
        for stats in value["containers"].values():
            stats["id"] = id
            id += 1


if __name__ == "__main__":
    main()


# json.loads(request.content) and request.json() is the same thing?

# http://{ip}:5000/container/<name>/start
