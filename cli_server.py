#!/usr/bin/env python3

# Server software which manipulates remote hosts with agents listening.

import requests
import pprint
import os

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
                ct_stats()
            case "2":
                ct_start()
            case "3":
                ct_stop()
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


def ct_stats():
    """
    Prints container stats from all hosts.
    """
    r = {
        key: value
        for ip in ips
        for key, value in requests.get(f"http://{ip}:5000/container/all").json().items()
    }

    pprint.pprint(r)

    input()


def ct_start():
    """
    Start a container by list id.
    """
    input("Coming soon...")


def ct_stop():
    """
    Stop a container by list id.
    """
    input("Coming soon...")


def hosts_api_stats():
    """
    Prints agent hosts api stats.
    """
    # Dict comprehension for creating "ip: api_stats" key-value pairs from ips.
    hosts = {ip: requests.get(f"http://{ip}:5000/stats").json() for ip in ips}

    pprint.pprint(hosts)
    input()


if __name__ == "__main__":
    main()


# json.loads(request.content) and request.json() is the same thing?
