import os
from dotenv import load_dotenv
import pandas as pd
import json
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from calendar import monthrange



load_dotenv()

# Use your direct API key
API_KEY = os.environ.get("CLOUDBEDS_API_KEY")

propertyIDs =[
    "214969",
    "295812",
    "215018",
    "317876",
    "318157"
]
monthlyStats = {}

# this number includes current month
monthNum = date.today().month
numMonthsLookAhead = 6
year = date.today().year 
# totalStartDate = date(year,1,1) - relativedelta(years=1)
totalStartDate = date.today()

validStatus = ["in_house", "not_checked_in", "checked_out"]
# data[rooms].roomCheckIn
def main():
    fillMonthStructure()
    reservationJSON = "../data/reservations.json"
    today = totalStartDate.strftime("%m-%d-%Y")
    outputName = f"{today}_{numMonthsLookAhead}_months"
    outputJSON = f"../data/{outputName}.json"
    with open(reservationJSON, "r", encoding="utf-8") as f:
        reservations = json.load(f)
    processData(reservations)
    calculateTotalStats()
    for month in list(monthlyStats.keys()):
        if monthlyStats[month]["occupancyPercent"] == 0:
            del monthlyStats[month]
    with open(outputJSON,"w", encoding="utf-8") as f:
        json.dump(monthlyStats,fp=f, indent=4)
    # createComprehensiveGraph(monthlyStats)


def processData(data):
    dateFormat = "%Y-%m-%d"
    fullDateFormat = "%Y-%m-%d %H:%M:%S"
    for row in data:
        # print(row)
        rooms = row["rooms"]
        # for each room reserved in the reservation
        for room in rooms:
            status = room["roomStatus"]
            startDate = room["roomCheckIn"]
            endDate = room["roomCheckOut"]
            startDateObject =  datetime.strptime(startDate, dateFormat).date()
            endDateObject =  datetime.strptime(endDate, dateFormat).date()
            yearMonth = startDateObject.strftime("%Y-%m")
            if(not isDateValid(startDateObject,endDateObject)): continue
            if(status not in validStatus):
                if yearMonth not in monthlyStats: continue
                monthlyStats[yearMonth]["cancelledReservations"] += 1
                continue
            # calulate the number of nights
            current_date = startDateObject
            while current_date < endDateObject:
                yearMonth = current_date.strftime("%Y-%m")
                if yearMonth not in monthlyStats: continue
                currDate = current_date.strftime(dateFormat)
                monthlyStats[yearMonth]["nightsRented"] += 1
                totalRevenue = room["detailedRoomRates"][currDate]
                monthlyStats[yearMonth]["totalRevenue"] += totalRevenue
                current_date += relativedelta(days=1)
            monthlyStats[yearMonth]["numReservations"] += 1

            dateBooked = datetime.strptime(row["dateCreated"], fullDateFormat).date()
            leadTime = (startDateObject - dateBooked).days
            monthlyStats[yearMonth]["totalBookingLeadTime"] += leadTime





def calculatePossibleNights(month):
    numUnits = 48
    daysInMonth = monthrange(month.year, month.month)
    possibleNights = daysInMonth[1] * numUnits
    return possibleNights

def fillMonthStructure():
    format = "%Y-%m"
    todayOneMonthInPast = totalStartDate - relativedelta(months=1)
    # formatted_date = today.strftime("%Y-%m")
    # account for month before and month after the range
    for i in range(numMonthsLookAhead + 2):
        monthToAdd = todayOneMonthInPast + relativedelta(months=i)
        monthFormatted = monthToAdd.strftime(format)
        monthDataPoints = {
            "occupancyPercent": 0,
            "nightsRented": 0,
            "numReservations":0,
            "cancelledReservations": 0,
            "cancelationRate" : 0,
            "possibleNights":0,
            "avgLengthOfStay" : 0,
            "totalRevenue" : 0,
            "possibleRevenue" : 0,
            "avgRevenue" : 0,
            "bookingLeadTime" : 0,
            "totalBookingLeadTime" : 0,
            "bookingLeadTime" : 0,
            "avgDailyRate" : 0,
            "revPAR" : 0,
        }
        monthlyStats[monthFormatted] = monthDataPoints

def isDateValid(checkInDate, checkOutDate):
    today = totalStartDate
    startOfThisMonth = date(today.year, today.month, 1)
    # grab the first day of the next month
    firstDayOfNextMonth = startOfThisMonth + relativedelta(months = numMonthsLookAhead)
    # subtract 1 to get the apropraite last day of month
    lastDayOfMonth = firstDayOfNextMonth - relativedelta(days=1)
    isCheckInInFuture = checkInDate >= lastDayOfMonth
    isCheckOutInPast = checkOutDate <= startOfThisMonth
    return not(isCheckInInFuture or isCheckOutInPast)
            
def calculateTotalStats():
    today = totalStartDate
    format = "%Y-%m"
    for i in range(numMonthsLookAhead):
        monthToCalculate = today + relativedelta(months=i)
        monthFormatted = monthToCalculate.strftime(format)
        possibleNights = calculatePossibleNights(monthToCalculate)
        nightsOccupied = monthlyStats[monthFormatted]["nightsRented"]
        occupancyRate = float(f"{((nightsOccupied / possibleNights) * 100):.2f}")
        monthlyStats[monthFormatted]["occupancyPercent"] = (occupancyRate)
        monthlyStats[monthFormatted]["possibleNights"] = possibleNights

        numResevations = monthlyStats[monthFormatted]["numReservations"]
        monthlyStats[monthFormatted]["avgLengthOfStay"] = float(f"{nightsOccupied / numResevations:.2f}")
        monthlyStats[monthFormatted]["totalRevenue"] = float(f"{monthlyStats[monthFormatted]["totalRevenue"]:.2f}")

        totalRevenue = monthlyStats[monthFormatted]["totalRevenue"]
        totalBookingLeadTime = monthlyStats[monthFormatted]["totalBookingLeadTime"]
        totalCancelations = monthlyStats[monthFormatted]["cancelledReservations"]
        monthlyStats[monthFormatted]["avgRevenue"] = float(f"{totalRevenue / numResevations:.2f}")
        monthlyStats[monthFormatted]["bookingLeadTime"] = float(f"{totalBookingLeadTime / numResevations:.2f}")
        monthlyStats[monthFormatted]["avgDailyRate"] = float(f"{totalRevenue / nightsOccupied:.2f}")
        monthlyStats[monthFormatted]["revPAR"] = float(f"{totalRevenue / possibleNights:.2f}")
        monthlyStats[monthFormatted]["possibleRevenue"] = float(f"{possibleNights * monthlyStats[monthFormatted]["avgDailyRate"]:.2f}")
        monthlyStats[monthFormatted]["cancelationRate"] = float(f"{totalCancelations / (totalCancelations + numResevations) * 100:.2f}")



if(__name__ == "__main__"):
    main()
