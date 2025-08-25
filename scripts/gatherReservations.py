import os
import sys
import json
import pandas as pd
import requests
from dotenv import load_dotenv
import math
from datetime import date, datetime

load_dotenv()

API_KEY = os.environ.get("CLOUDBEDS_API_KEY")

propertyIDs =[
    "214969",
    "295812",
    "215018",
    "317876",
    "318157"
]

def getReservations():
    # create endpoint
    baseUrl = "https://api.cloudbeds.com/api/v1.3/"
    baseEndpoint = "getReservation"
    additionalEndPoint = "sWithRateDetails"
    endPoint = baseEndpoint + additionalEndPoint
    fullEndPoint = f"{baseUrl}{endPoint}"

    # pass in headers
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "accept": "application/json"
    }

    outputPath = "../data/reservations.json"

    # clear the json
    with open (outputPath, "w", encoding="utf-8", newline="") as f:
        pass

    # figure out how many calls we need
    loops = initalCall(fullEndPoint,headers)

    allReservations = []
    for i in range(0,loops):
        # params to be sent to the call
        params = {
            "propertyID": propertyIDs[0],
            "pageNumber": i + 1,
            "includeAllRooms" : True,
            "resultsFrom" : date(2020,1,1)
        }
        data = apiCall(fullEndPoint=fullEndPoint,headers=headers,params=params)
        print(f"\r{i}/{loops} pages complete        ", end="")
        allReservations.extend(data)
    with open (outputPath, "a", encoding="utf-8", newline="") as f:
            json.dump(allReservations, f, indent = 4)


# this is the intial API call to figure out how many calls we need in total
# returns (total count, count per page)
def initalCall(fullEndPoint, headers):
    # pass in inital parameters
    initParams = {
        "propertyID": propertyIDs[0],
        "resultsFrom" : date(2020,1,1)
    }
    # grab response and convert to JSON
    response = requests.get(url=fullEndPoint, headers=headers, params=initParams)
    resJSON = response.json()
    totalCount = resJSON["total"]
    countPerPage = resJSON["count"]
    print(f"{totalCount} total entries")
    print(f"{countPerPage} per page")
    # take the ceiling to ensure we dont miss any data
    loops = math.ceil(totalCount/countPerPage)

    return loops

def apiCall(fullEndPoint,headers, params):
    response = requests.get(url=fullEndPoint, headers=headers, params=params)
    resJSON = response.json()
    if resJSON["success"] != True:
            print(f"something went wrong")
            return
    data = resJSON["data"]
    return data

if(__name__ == "__main__"):
    # testBlockedDates()
    getReservations()