# By James Robertson for csc8110

from __future__ import division
from pymongo import MongoClient
import sys
import signal
import csv
import re
import time
import datetime
import thread
import requests
import numpy as np

client = MongoClient("mongodb://admin:password@localhost:3306")
db = client.primecheck
collection = db.responses

x = collection.delete_many({})
print str(x.deleted_count) + " responses purged."

url = "" # sys.argv[1]

concurrent = 1 # sys.argv[5]

flag = "" # sys.argv[6]

def signal_handler(sig, frame):
    generate_csv()
    print "Complete!"
    sys.exit(0)

def generate_csv():
    print "Generating results file..."
    with open("responses_" + flag + ".csv", mode="w") as response_file:
        response_writer = csv.writer(response_file, delimiter=",")
        for x in collection.find({}):
            response_writer.writerow([x["_id"], x["response"]])

def normal(mu, sigma):
    while True:
        delay = max(0, np.random.normal(mu, sigma))
        print "Waiting " + str(delay) + " seconds..."
        time.sleep(delay)
        for c in range(concurrent):
            print "Making request."
            thread.start_new_thread(get, ())
    return

def poisson(lam, k):
    while True:
        req_count = np.random.poisson(lam)
        print "Making " + str(req_count * concurrent) + " requests in the next " + str(k) + "  seconds."
        delay = k / max(0, req_count)
        for i in range(req_count):
            print "(" + str(i + 1) + "/" + str(req_count) + ") Waiting " + str(delay) + " seconds..."
            time.sleep(delay)
            for c in range(concurrent):
                print "Making request."
                thread.start_new_thread(get, ())
    return

def get():
    date = str(datetime.datetime.now())
    resp = re.search("\d+", requests.get(url).text).group()
    json = {"_id" : date, "response" : resp}
    try:
        post_id = collection.insert_one(json).inserted_id
        print "(Recorded value of " + resp + " requested at time " + date + ")"
    except:
        print "oops"

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    if len(sys.argv) >= 7:
        flag = sys.argv[6]
    if len(sys.argv) >= 6:
        concurrent = int(sys.argv[5])
    if len(sys.argv) >= 5 and sys.argv[2] == "normal":
        url = sys.argv[1]
        normal(float(sys.argv[3]), float(sys.argv[4]))
    elif len(sys.argv) >= 5 and sys.argv[2] == "poisson":
        url = sys.argv[1]
        poisson(float(sys.argv[3]), float(sys.argv[4]))
    else:
        print "Invalid args!"
