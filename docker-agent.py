import docker
client = docker.from_env()
while True:
    n = int(input("\n What info is looked for? \n 1. Status Check \n 2. Start Container \n 3. Stop Container \n 4. "))
    if n == 1:
        containers = client.containers.list()
        for container in containers:
            stats = container.stats(stream=False)  # stream=False gives a single snapshot of stats

                # Print some key stats (customize as per your need)
            print(f"Container: {container.name}", f"CPU Usage: {stats['cpu_stats']['cpu_usage']['total_usage']}", f"Memory Usage: {stats['memory_stats']['usage']}", f"Network I/O: {stats['networks']}")
            #print("\n ")
    elif n == 2:
        print("WIP")
    elif n == 3:
        print("WIP")
    else:
        print("Give working Option")

        client.api.info()
        

    #print(client.api.stats())
    
    # #Test för multipla Frågor
    # n = int(input("What info is looked for?"))
    # if n == 1:
    #     client.containers.list()
    # elif n== 2:
    #     print("hejsan")
    # elif n== 3:
    #     print("hej då")
    # else:
    #     print(client.api.containers.())