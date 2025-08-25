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
    # where the reservation data is being stored (JSON)
    reservationJSON = "../data/reservations.json"
    # format the start date
    today = totalStartDate.strftime("%m-%d-%Y")
    
    # create output json name based on todays date
    outputName = f"{today}_{numMonthsLookAhead}_months"
    outputJSON = f"../data/{outputName}.json"

    # load the reservations into reservations variable
    with open(reservationJSON, "r", encoding="utf-8") as f:
        reservations = json.load(f)

    processData(reservations)
    
    # this function calcultes overall statistics for the reservations
    calculateTotalStats()

    # remove any entries that are blank, this is used to remove the padding months
    # padding months are the extra month before and after the period of reservations that is being serarched, this was added to account for reservations going into and leaving the period we are seatching

    for month in list(monthlyStats.keys()):
        if monthlyStats[month]["occupancyPercent"] == 0:
            del monthlyStats[month]

    # write data to output
    with open(outputJSON,"w", encoding="utf-8") as f:
        json.dump(monthlyStats,fp=f, indent=4)


def processData(data):
    dateFormat = "%Y-%m-%d"
    fullDateFormat = "%Y-%m-%d %H:%M:%S"
    for row in data:
        rooms = row["rooms"]
        # for each room reserved in the reservation
        for room in rooms:
            # grab data
            status = room["roomStatus"]
            startDate = room["roomCheckIn"]
            endDate = room["roomCheckOut"]

            # format dates
            startDateObject =  datetime.strptime(startDate, dateFormat).date()
            endDateObject =  datetime.strptime(endDate, dateFormat).date()
            yearMonth = startDateObject.strftime("%Y-%m")
            
            # if the reservation is not in the period we are searching, skip it
            if(not isDateValid(startDateObject,endDateObject)): continue
            
            # if the reseration is cancelled count it and skip it
            if(status not in validStatus):
                if yearMonth not in monthlyStats: continue
                monthlyStats[yearMonth]["cancelledReservations"] += 1
                continue
            # calulate the number of nights
            # this is done by walking the dates day by day, determining which month we are currently in and split reservations that way
            current_date = startDateObject
            # while reseravtion is not over
            while current_date < endDateObject:
                yearMonth = current_date.strftime("%Y-%m")
                # if somehow the year/month we are in is not in our searching period, skip it
                # this is just an extra safety check
                if yearMonth not in monthlyStats: continue
                
                # format the current date
                currDate = current_date.strftime(dateFormat)

                # increment stats
                monthlyStats[yearMonth]["nightsRented"] += 1
                totalRevenue = room["detailedRoomRates"][currDate]
                monthlyStats[yearMonth]["totalRevenue"] += totalRevenue
                current_date += relativedelta(days=1)
            monthlyStats[yearMonth]["numReservations"] += 1

            dateBooked = datetime.strptime(row["dateCreated"], fullDateFormat).date()
            leadTime = (startDateObject - dateBooked).days
            monthlyStats[yearMonth]["totalBookingLeadTime"] += leadTime





def calculatePossibleNights(month):
    # we currently have 48 units, this will need to be adjusted if any are added or removed
    numUnits = 48

    # how many days are in the current month?
    daysInMonth = monthrange(month.year, month.month)

    # grab the number of days we have in the months and multiply by the number of units we have
    possibleNights = daysInMonth[1] * numUnits
    return possibleNights

# this is used to fill the inital JSON structure
def fillMonthStructure():
    format = "%Y-%m"

    # go one in the past to add a padding month, this is for reservations that check in before the period but checkout in the period
    todayOneMonthInPast = totalStartDate - relativedelta(months=1)
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

# returns true if valid date and false otherwise
def isDateValid(checkInDate, checkOutDate):
    today = totalStartDate
    startOfThisMonth = date(today.year, today.month, 1)
    # grab the first day of the next month
    firstDayOfNextMonth = startOfThisMonth + relativedelta(months = numMonthsLookAhead)
    # subtract 1 to get the apropraite last day of month
    lastDayOfMonth = firstDayOfNextMonth - relativedelta(days=1)

    # check if the check out is in the past or in the future
    isCheckInInFuture = checkInDate >= lastDayOfMonth
    isCheckOutInPast = checkOutDate <= startOfThisMonth
    return not(isCheckInInFuture or isCheckOutInPast)
            

# this is used to geenrate overall stats for the reservations
def calculateTotalStats():
    today = totalStartDate
    format = "%Y-%m"
    # for each month
    for i in range(numMonthsLookAhead):
        # grab curent month
        monthToCalculate = today + relativedelta(months=i)
        monthFormatted = monthToCalculate.strftime(format)
        
        # how many possible nights do we have in this month
        possibleNights = calculatePossibleNights(monthToCalculate)

        # grab needed metrics for the stats
        nightsOccupied = monthlyStats[monthFormatted]["nightsRented"]
        numResevations = monthlyStats[monthFormatted]["numReservations"]
        totalBookingLeadTime = monthlyStats[monthFormatted]["totalBookingLeadTime"]
        totalCancelations = monthlyStats[monthFormatted]["cancelledReservations"]
        totalRevenue = monthlyStats[monthFormatted]["totalRevenue"]

        # calculate key metrics
        occupancyRate = float(f"{((nightsOccupied / possibleNights) * 100):.2f}")
        monthlyStats[monthFormatted]["occupancyPercent"] = occupancyRate
        monthlyStats[monthFormatted]["avgLengthOfStay"] = float(f"{nightsOccupied / numResevations:.2f}")
        monthlyStats[monthFormatted]["totalRevenue"] = float(f"{monthlyStats[monthFormatted]["totalRevenue"]:.2f}")
        monthlyStats[monthFormatted]["possibleNights"] = possibleNights
        monthlyStats[monthFormatted]["avgRevenue"] = float(f"{totalRevenue / numResevations:.2f}")
        monthlyStats[monthFormatted]["bookingLeadTime"] = float(f"{totalBookingLeadTime / numResevations:.2f}")
        monthlyStats[monthFormatted]["avgDailyRate"] = float(f"{totalRevenue / nightsOccupied:.2f}")
        monthlyStats[monthFormatted]["revPAR"] = float(f"{totalRevenue / possibleNights:.2f}")
        monthlyStats[monthFormatted]["possibleRevenue"] = float(f"{possibleNights * monthlyStats[monthFormatted]["avgDailyRate"]:.2f}")
        monthlyStats[monthFormatted]["cancelationRate"] = float(f"{totalCancelations / (totalCancelations + numResevations) * 100:.2f}")

if(__name__ == "__main__"):
    main()
