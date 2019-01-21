# By James Robertson for csc8110

import sys
import signal
import time
import json
import csv
import requests
from pymongo import MongoClient

client = MongoClient("mongodb://admin:password@localhost:3306")
db = client.primecheck
collection = db.stats

x = collection.delete_many({})
print str(x.deleted_count) + " statistics purged."

rest_point = "/api/v1.3/subcontainers/docker/"

url = "http://localhost:888" #argv[1]

containers = ["a2", "5c"] #argv[2]

flag = "" #argv[3]

class Statistic:
    def __init__(self, timestamp, cpu, memory, io, container):
        self.timestamp = timestamp
        self.cpu = cpu
        self.memory = memory
        self.io = io
        self.container = container

    def get_json(self):
        return {"_id" : self.timestamp,
        "cpu" : self.cpu,
        "memory" : self.memory,
        "io" : self.io,
        "container" : self.container,
        "flag" : flag}

def signal_handler(sig, frame):
    sys.stdout.write("\033[K")
    generate_csv()
    print "Complete!"
    sys.exit(0)

def generate_csv():
    print "Generating results file..."
    for container in containers:
        with open("results_" + flag + "_" + container + ".csv", mode="w") as result_file:
            result_writer = csv.writer(result_file, delimiter=",")
            for x in collection.find({ "container" : container }):
                result_writer.writerow([x["_id"], 
                    x["cpu"], 
                    x["memory"], 
                    x["io"], 
                    x["container"], 
                    x["flag"]])

def get_statistics():
    while True:
        print "Gathering statistics: "
        for container in containers:
            stats = requests.get(url + rest_point + container).json()[0]["stats"]
        
            for stat in stats:
                timestamp = stat["timestamp"]
                cpu = stat["cpu"]["usage"]["total"]
                memory = stat["memory"]["usage"]
                io = 0
                if len(stat["diskio"]) != 0:
                    io = stat["diskio"]["io_serviced"][0]["stats"]["Total"]

                s = Statistic(timestamp, cpu, memory, io, container)

                try:
                    post_id = collection.insert_one(s.get_json()).inserted_id
                    print "Recorded values at " + post_id + " for container " + container + "."
                except:
                    pass
                    #print s.timestamp + " already recorded for container " + container + "."
        for i in range(5):
            print "Gathering next statistics in " + str(5 - i) + "..."
            sys.stdout.write("\033[F")
            time.sleep(1)
        sys.stdout.write("\033[K")

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)

    url = sys.argv[1]
    containers = sys.argv[2].split(",")
    if len(sys.argv) == 4:
        flag = sys.argv[3]

    get_statistics()
