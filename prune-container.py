import docker
client = docker.from_env()

#@app.route("/container/all/prune", methods=["Get"])
def prune1():
    #a api endpoint for pruning containers.

    
    #this will prune the containers
    prune = client.containers.prune()
    prune
    return"containers have been pruned"    
prune1()