import docker
client = docker.from_env()

@app.route("/container/all/prune", methods=["Get"])
def prune():
    #a api endpoint for pruning containers.

    #list with containers
    list = client.containers.list()
    #this will prune the containers
    prune = client.containers.prune()
    prune(license)
    return(" containers have been pruned")
    
