import json
import csv
import sys
import os
import re


def main():
    csvPath = "../data/occup_rate_012024-082025.csv"
    csvSplit = re.split("[.]",csvPath)
    dataJsonPath = "../data/09-16-2025_4_months.json"

    with open(csvPath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        with open(dataJsonPath, "r", encoding="utf-8", newline="") as f:
            jsonObject = json.load(f)
        for row in reader:
            year = row["Year"]
            month = row["Month"] if len(row["Month"]) == 2 else "0" + row["Month"]
            occupancy = row["Occupancy"]
            nightsOccupied = row["NightsOccupied"]
            yearMonth = year + "-" + month
            if yearMonth not in jsonObject:
                jsonObject[yearMonth] = {
                    "occupancyPercent" : int(occupancy),
                    "nightsRented" : int(nightsOccupied)
                }

    with open(dataJsonPath, "w", encoding="utf-8", newline="") as f:
        json.dump(jsonObject, f, indent=4)
            
if __name__ == "__main__":
    main()