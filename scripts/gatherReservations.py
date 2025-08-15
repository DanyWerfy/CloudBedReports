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
    outputPath = "../data/reservations.json"
    # clear the json
    with open (outputPath, "w", encoding="utf-8", newline="") as f:
        pass
    baseUrl = "https://api.cloudbeds.com/api/v1.3/"
    endpoint = "getReservation"
    additionalEndPoint = "sWithRateDetails"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "accept": "application/json"
    }

    initParams = {
        "propertyID": propertyIDs[0],
        "resultsFrom" : date(2020,1,1)

    }
    finalEndPoint = endpoint + additionalEndPoint
    fullURL = f"{baseUrl}{finalEndPoint}"
    response = requests.get(url=fullURL, headers=headers, params=initParams)
    resJSON = response.json()
    totalCount = resJSON["total"]
    countPerPage = resJSON["count"]
    print(f"{totalCount} total entries")
    print(f"{countPerPage} per page")
    loops = math.ceil(totalCount/countPerPage)
    allReservations = []
    for i in range(0,loops):
        params = {
            "propertyID": propertyIDs[0],
            "pageNumber": i + 1,
            "includeAllRooms" : True,
            "resultsFrom" : date(2020,1,1)
        }
        response = requests.get(url=fullURL, headers=headers, params=params)
        resJSON = response.json()
        if resJSON["success"] != True:
             print(f"something went wrong")
             return
        data = resJSON["data"]
        print(f"\r{i}/{loops} pages complete        ", end="")
        allReservations.extend(data)
    with open (outputPath, "a", encoding="utf-8", newline="") as f:
            json.dump(allReservations, f, indent = 4)

def testBlockedDates():
    outputPath = "../data/blockedDates.json"
    # clear the json
    with open (outputPath, "w", encoding="utf-8", newline="") as f:
        pass
    baseUrl = "https://api.cloudbeds.com/api/v1.3/"
    endpoint = "getRoom"
    additionalEndPoint = "Blocks"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "accept": "application/json",
    }

    initParams = {
        "propertyID": propertyIDs[0]
    }
    finalEndPoint = endpoint + additionalEndPoint
    fullURL = f"{baseUrl}{finalEndPoint}"
    response = requests.get(url=fullURL, headers=headers, params=initParams)
    resJSON = response.json()
    countPerPage = resJSON["count"]
    print(f"{countPerPage} per page")
    loops = 1
    allReservations = []
    for i in range(0,loops):
        params = {
            "propertyID": propertyIDs[0],
            "pageNumber": i,
            "startDate": date(2025,8,1),
            "endDate": date(2025,8,31)
        }
        response = requests.get(url=fullURL, headers=headers, params=params)
        resJSON = response.json()["data"]
        print(f"\r{i}/{loops} pages complete        ", end="")
        allReservations.extend(resJSON)
    with open (outputPath, "a", encoding="utf-8", newline="") as f:
            json.dump(resJSON, f, indent = 4)


if(__name__ == "__main__"):
    # testBlockedDates()
    getReservations()