# By James Robertson for csc8110

import docker
import time

client = docker.from_env()
try:
    client.swarm.leave(True)
except:
    pass
client.swarm.init()

# Primecheck instances
spec = docker.types.EndpointSpec(ports={80: (8080, "tcp")})
restart = docker.types.RestartPolicy("on-failure")
primecheck = client.services.create(
    "nclcloudcomputing/javabenchmarkapp:latest",
    name="primecheck",
    restart_policy=restart,
    endpoint_spec=spec,
    env=["SERVICE_PORTS=8080"]
)
primecheck.reload()
primecheck.scale(2)

#Proxy instance
#spec = docker.types.EndpointSpec(ports={80: (80, "tcp")})
#restart = docker.types.RestartPolicy("on-failure")
#client.services.create(
#    "dockercloud/haproxy",
#    name="proxy",
#    restart_policy=restart,
#    endpoint_spec=spec,
#    mounts=["/var/run/docker.sock:/var/run/docker.sock"],
#    env=["BALANCE=leastconn"],
#    constraints=["node.role == manager"]
#)

# Visualiser instance
spec = docker.types.EndpointSpec(ports={88: (8080, "tcp")})
restart = docker.types.RestartPolicy("on-failure")
client.services.create(
    "dockersamples/visualizer:stable",
    name="visualiser",
    restart_policy=restart,
    endpoint_spec=spec,
    mounts=["/var/run/docker.sock:/var/run/docker.sock"],
    constraints=["node.role == manager"]
)

# Mongo instance
spec = docker.types.EndpointSpec(ports={3306: (27017, "tcp")})
restart = docker.types.RestartPolicy("on-failure")
client.services.create(
    "mongo",
    name="database",
    restart_policy=restart,
    endpoint_spec=spec,
    env=[
        "MONGO_INITDB_ROOT_USERNAME=admin", 
        "MONGO_INITDB_ROOT_PASSWORD=password"
    ]
)

# Cadvisor instance
spec = docker.types.EndpointSpec(ports={888: (8080, "tcp")})
restart = docker.types.RestartPolicy("on-failure")
client.services.create(
    "google/cadvisor:latest",
    name="cadvisor",
    restart_policy=restart,
    endpoint_spec=spec,
    mounts=[
        "/:/rootfs:ro",
        "/var/run:/var/run:rw",
        "/sys:/sys:ro",
        "/var/lib/docker/:/var/lib/docker:ro"
    ]
)
