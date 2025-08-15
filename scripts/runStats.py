import requests
import os
from dotenv import load_dotenv
import pandas as pd
import json
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from calendar import monthrange
import math
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

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
numMonthsLookAhead = 6


validStatus = ["in_house", "not_checked_in", "checked_out"]
# data[rooms].roomCheckIn
def main():
    fillMonthStructure()
    reservationJSON = "../data/reservations.json"
    today = date.today().strftime("%m-%d-%Y")
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
                monthlyStats[yearMonth]["cancelledReservations"] += 1
                continue
            # calulate the number of nights
            current_date = startDateObject
            while current_date < endDateObject:
                yearMonth = current_date.strftime("%Y-%m")
                currDate = current_date.strftime(dateFormat)
                if yearMonth in monthlyStats:
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
    todayOneMonthInPast = date.today() - relativedelta(months=1)
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
    today = date.today()
    startOfThisMonth = date(today.year, today.month, 1)
    # grab the first day of the next month
    firstDayOfNextMonth = startOfThisMonth + relativedelta(months = numMonthsLookAhead)
    # subtract 1 to get the apropraite last day of month
    lastDayOfMonth = firstDayOfNextMonth - relativedelta(days=1)
    isCheckInInFuture = checkInDate >= lastDayOfMonth
    isCheckOutInPast = checkOutDate <= startOfThisMonth
    return not(isCheckInInFuture or isCheckOutInPast)
            
def calculateTotalStats():
    today = date.today()
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




def createGraph(monthlyStats):
    # Convert the dictionary to a Pandas DataFrame
    df_monthly_stats = pd.DataFrame.from_dict(monthlyStats, orient='index')
    df_monthly_stats.index.name = 'Month'
    df_monthly_stats.reset_index(inplace=True)

    # Create a figure with a 2x2 subplot layout where the top chart spans two columns
    fig = make_subplots(
        rows=2, cols=2,
        shared_xaxes=False,
        vertical_spacing=0.1,
        specs=[[{"colspan": 2}, None], [{}, {}]]
    )

    # Add the first trace (Occupancy Percentage) as a bar chart, spanning two columns
    fig.add_trace(
        go.Bar(
            x=df_monthly_stats['Month'],
            y=df_monthly_stats['occupancyPercent'],
            name='Occupancy Percentage',
            marker_color='mediumseagreen',
        ),
        row=1, col=1
    )

    # Add the second trace (Number of Reservations) as a bar chart
    fig.add_trace(
        go.Bar(
            x=df_monthly_stats['Month'],
            y=df_monthly_stats['numReservations'],
            name='Number of Reservations',
            marker_color='cornflowerblue',
        ),
        row=2, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=df_monthly_stats['Month'],
            y=df_monthly_stats['avgLengthOfStay'],
            name='Average Length of Stay',
            mode='lines+markers',
            marker_color='firebrick',
        ),
        row=2, col=2
    )

    # Update the layout for a clean appearance and increased height
    fig.update_layout(
        title_text="Monthly Occupancy, Reservations, and Average Stay",
        title_x=0.5,
        height=900
    )

    # Update y-axis titles for each subplot
    fig.update_yaxes(title_text="Occupancy Percentage (%)", row=1, col=1)
    fig.update_yaxes(title_text="Number of Reservations", row=2, col=1)
    fig.update_yaxes(title_text="Average Length of Stay", row=2, col=2)

    fig.show()

def createComprehensiveGraph(monthlyStats):
    # Convert the dictionary to a Pandas DataFrame
    df_monthly_stats = pd.DataFrame.from_dict(monthlyStats, orient='index')
    df_monthly_stats.index.name = 'Month'
    df_monthly_stats.reset_index(inplace=True)
    
    # Create a comprehensive dashboard with 3x3 subplot layout
    fig = make_subplots(
        rows=3, cols=3,
        subplot_titles=(
            'Occupancy Rate (%)', 'Actual vs Possible Revenue ($)', 'Nights Rented vs Possible',
            'Number of Reservations', 'Average Daily Rate & RevPAR ($)', 'Average Revenue per Reservation ($)',
            'Average Length of Stay (Days)', 'Booking Lead Time (Days)', 'Revenue Realization Rate (%)'
        ),
        specs=[
            [{"secondary_y": False}, {"secondary_y": False}, {"secondary_y": False}],
            [{"secondary_y": False}, {"secondary_y": True}, {"secondary_y": False}],
            [{"secondary_y": False}, {"secondary_y": False}, {"secondary_y": False}]
        ],
        vertical_spacing=0.08,
        horizontal_spacing=0.08
    )

    # 1. Occupancy Rate - Bar chart (performance metric)
    fig.add_trace(
        go.Bar(
            x=df_monthly_stats['Month'],
            y=df_monthly_stats['occupancyPercent'],
            name='Occupancy %',
            marker_color='mediumseagreen',
            showlegend=False
        ),
        row=1, col=1
    )

    # 2. Actual vs Possible Revenue - Side by side bar chart

    
    fig.add_trace(
        go.Bar(
            x=df_monthly_stats['Month'],
            y=df_monthly_stats['totalRevenue'],
            name='Actual Revenue',
            marker_color='darkblue',
            showlegend=False,
            offsetgroup=2
        ),
        row=1, col=2
    )

    fig.add_trace(
        go.Bar(
            x=df_monthly_stats['Month'],
            y=df_monthly_stats['possibleRevenue'],
            name='Possible Revenue',
            marker_color='lightblue',
            opacity=0.7,
            showlegend=False,
            offsetgroup=1
        ),
        row=1, col=2
    )

    # 3. Nights Rented vs Possible - Side by side bar chart
    fig.add_trace(
        go.Bar(
            x=df_monthly_stats['Month'],
            y=df_monthly_stats['nightsRented'],
            name='Nights Rented',
            marker_color='steelblue',
            showlegend=False,
            offsetgroup=1
        ),
        row=1, col=3
    )
    
    fig.add_trace(
        go.Bar(
            x=df_monthly_stats['Month'],
            y=df_monthly_stats['possibleNights'],
            name='Possible Nights',
            marker_color='lightgray',
            showlegend=False,
            offsetgroup=2
        ),
        row=1, col=3
    )

    # 4. Number of Reservations - Bar chart (volume metric)
    fig.add_trace(
        go.Bar(
            x=df_monthly_stats['Month'],
            y=df_monthly_stats['numReservations'],
            name='Reservations',
            marker_color='cornflowerblue',
            showlegend=False
        ),
        row=2, col=1
    )

    # 5. Average Daily Rate & RevPAR - Dual axis chart
    fig.add_trace(
        go.Scatter(
            x=df_monthly_stats['Month'],
            y=df_monthly_stats['avgDailyRate'],
            mode='lines+markers',
            name='Avg Daily Rate',
            line_color='orange',
            marker_size=8,
            showlegend=False
        ),
        row=2, col=2
    )
    
    fig.add_trace(
        go.Scatter(
            x=df_monthly_stats['Month'],
            y=df_monthly_stats['revPAR'],
            mode='lines+markers',
            name='RevPAR',
            line_color='red',
            marker_size=8,
            yaxis='y2',
            showlegend=False
        ),
        row=2, col=2, secondary_y=True
    )

    # 6. Average Revenue per Reservation - Line chart (efficiency metric)
    fig.add_trace(
        go.Scatter(
            x=df_monthly_stats['Month'],
            y=df_monthly_stats['avgRevenue'],
            mode='lines+markers',
            name='Avg Revenue/Reservation',
            line_color='purple',
            marker_size=8,
            showlegend=False
        ),
        row=2, col=3
    )

    # 7. Average Length of Stay - Line chart (guest behavior)
    fig.add_trace(
        go.Scatter(
            x=df_monthly_stats['Month'],
            y=df_monthly_stats['avgLengthOfStay'],
            mode='lines+markers',
            name='Avg Length of Stay',
            line_color='firebrick',
            marker_size=8,
            showlegend=False
        ),
        row=3, col=1
    )

    # 8. Booking Lead Time - Line chart (booking behavior trend)
    fig.add_trace(
        go.Scatter(
            x=df_monthly_stats['Month'],
            y=df_monthly_stats['bookingLeadTime'],
            mode='lines+markers',
            name='Booking Lead Time',
            line_color='darkcyan',
            marker_size=8,
            showlegend=False
        ),
        row=3, col=2
    )

    # 9. Revenue Realization Rate - Line chart with percentage
    realization_rate = (df_monthly_stats['totalRevenue'] / df_monthly_stats['possibleRevenue']) * 100
    fig.add_trace(
        go.Scatter(
            x=df_monthly_stats['Month'],
            y=realization_rate,
            mode='lines+markers',
            name='Revenue Realization %',
            line_color='purple',
            marker_size=10,
            showlegend=False
        ),
        row=3, col=3
    )

    # Update layout
    fig.update_layout(
        title_text="Comprehensive Hotel GriffinTown Analytics",
        title_x=0.5,
        height=1200,
        font_size=10,
        barmode='stack'  # For the stacked bar chart
    )

    # Update y-axis titles and formatting
    fig.update_yaxes(title_text="Percentage", row=1, col=1)
    fig.update_yaxes(title_text="Revenue ($)", tickformat='$,.0f', row=1, col=2)
    fig.update_yaxes(title_text="Nights", row=1, col=3)
    fig.update_yaxes(title_text="Count", row=2, col=1)
    fig.update_yaxes(title_text="ADR ($)", tickformat='$,.0f', row=2, col=2)
    fig.update_yaxes(title_text="RevPAR ($)", tickformat='$,.0f', row=2, col=2, secondary_y=True)
    fig.update_yaxes(title_text="Revenue ($)", tickformat='$,.0f', row=2, col=3)
    fig.update_yaxes(title_text="Days", row=3, col=1)
    fig.update_yaxes(title_text="Days", row=3, col=2)
    fig.update_yaxes(title_text="Percentage (%)", row=3, col=3)

    # Rotate x-axis labels for better readability
    fig.update_xaxes(tickangle=45)

    fig.show()

    
if(__name__ == "__main__"):
    main()
