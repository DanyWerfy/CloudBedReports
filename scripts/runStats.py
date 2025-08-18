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
numMonthsLookAhead = 24
year = date.today().year 
totalStartDate = date(year,1,1) - relativedelta(years=1)

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
    createGraph(monthlyStats)


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




def createGraph(monthlyStats):

    # Convert the dictionary to a Pandas DataFrame
    df_monthly_stats = pd.DataFrame.from_dict(monthlyStats, orient='index')
    df_monthly_stats.index.name = 'Month'
    df_monthly_stats.reset_index(inplace=True)

    # Convert the 'Month' string to a datetime object and extract year and month name
    df_monthly_stats['Month'] = pd.to_datetime(df_monthly_stats['Month'])
    df_monthly_stats['Year'] = df_monthly_stats['Month'].dt.year
    df_monthly_stats['MonthName'] = df_monthly_stats['Month'].dt.strftime('%b')

    # Create a figure with a 2x2 subplot layout
    fig = make_subplots(
        rows=2, cols=2,
        shared_xaxes=False,
        vertical_spacing=0.1,
        specs=[[{"colspan": 2}, None], [{}, {}]]
    )

    # Define color schemes for each chart
    year_colors = {
        2024: ("#5F768E", "#B0C4DE"),
        2025: ("#8B4513", "#D2B48C")
    }

    # Add the first chart: Occupancy Percentage
    add_bar_chart(fig, 1, 1, 'occupancyPercent', 'Occupancy', year_colors, df_monthly_stats)

    # Add the second chart: Number of Reservations
    add_bar_chart(fig, 2, 1, 'numReservations', 'Reservations', year_colors, df_monthly_stats)

    # Add the third chart: Average Length of Stay
    add_line_chart(fig, 2, 2, 'avgLengthOfStay', 'Avg Stay', year_colors, df_monthly_stats)
    fig.add_vline(
        x=(date.today() - relativedelta(months=1)).month, 
        line_width = 3, 
        line_dash ="dash", 
        line_color = "grey",
        annotation_text = "Today",
        annotation_position ="top left",
        annotation=dict(font_size=15),
        annotation_font_color = "black"
        
    )

    # Update the layout for a clean appearance and increased height
    fig.update_layout(
        title_text="Monthly Occupancy, Reservations, and Average Stay Comparison (2024 vs 2025)",
        title_x=0.5,
        height=900,
        plot_bgcolor="#F5F5DC",
        paper_bgcolor="#FFFFFF"
    )

    # Update y-axis titles for each subplot
    fig.update_yaxes(title_text="Occupancy Percentage (%)", row=1, col=1)
    fig.update_yaxes(title_text="Number of Reservations", row=2, col=1)
    fig.update_yaxes(title_text="Average Length of Stay (Days)", row=2, col=2)
    fig.update_xaxes(showgrid=False) # Removes vertical gridlines

    fig.show()
def createComprehensiveGraph(monthlyStats):
    # Convert the dictionary to a Pandas DataFrame
    df_monthly_stats = pd.DataFrame.from_dict(monthlyStats, orient='index')
    df_monthly_stats.index.name = 'Month'
    df_monthly_stats.reset_index(inplace=True)

    # Parse month to datetime and extract year, month name
    df_monthly_stats['Month'] = pd.to_datetime(df_monthly_stats['Month'])
    df_monthly_stats['Year'] = df_monthly_stats['Month'].dt.year
    df_monthly_stats['MonthName'] = df_monthly_stats['Month'].dt.strftime('%b')

    today = pd.to_datetime("2025-08-18")  # or date.today()

    # Create a comprehensive dashboard with 3x3 subplot layout
    fig = make_subplots(
        rows=3, cols=3,
        subplot_titles=(
            'Occupancy Rate (%)', 'Actual vs Possible Revenue ($)', 'Nights Rented vs Possible',
            'Number of Reservations', 'Average Daily Rate ($)', 'RevPAR ($)',
            'Average Revenue per Reservation ($)', 'Average Length of Stay (Days)', 'Booking Lead Time (Days)'
        ),
        specs=[
            [{"secondary_y": False}, {"secondary_y": False}, {"secondary_y": False}],
            [{"secondary_y": False}, {"secondary_y": False}, {"secondary_y": False}],
            [{"secondary_y": False}, {"secondary_y": False}, {"secondary_y": False}]
        ],
        vertical_spacing=0.08,
        horizontal_spacing=0.08
    )

    # Year colors: (future/bold, past/faded)
    year_colors = {
        2024: ("#5F768E", "#B0C4DE"),
        2025: ("#8B4513", "#D2B48C")
    }

    # Helper for bar charts





    # 1. Occupancy Rate
    add_bar_chart(fig,1, 1, 'occupancyPercent', "Occupancy %", year_colors, df_monthly_stats)

    # 2. Actual vs Possible Revenue
    add_bar_chart(fig,1, 2, 'totalRevenue', "Actual Revenue", year_colors, df_monthly_stats)
    add_bar_chart(fig,1, 2, 'possibleRevenue', "Possible Revenue", year_colors, df_monthly_stats)

    # 3. Nights Rented vs Possible
    add_bar_chart(fig,1, 3, 'nightsRented', "Nights Rented", year_colors, df_monthly_stats)
    add_bar_chart(fig,1, 3, 'possibleNights', "Possible Nights", year_colors, df_monthly_stats)

    # 4. Number of Reservations
    add_bar_chart(fig,2, 1, 'numReservations', "Reservations", year_colors, df_monthly_stats)

    # 5. Average Daily Rate
    add_line_chart(fig,2, 2, 'avgDailyRate', "Avg Daily Rate", year_colors, df_monthly_stats)

    # 6. RevPAR
    add_line_chart(fig,2, 3, 'revPAR', "RevPAR", year_colors, df_monthly_stats)

    # 7. Average Revenue per Reservation
    add_line_chart(fig,3, 1, 'avgRevenue', "Avg Revenue/Reservation", year_colors, df_monthly_stats)

    # 8. Average Length of Stay
    add_line_chart(fig,3, 2, 'avgLengthOfStay', "Avg Length of Stay", year_colors, df_monthly_stats)

    # 9. Booking Lead Time
    add_line_chart(fig,3, 3, 'bookingLeadTime', "Booking Lead Time", year_colors, df_monthly_stats)
    today_month = today.month - 1  # Get 0-indexed month
    
    # Loop through each subplot and add the vertical line
    fig.add_vline(
        x=today_month, 
        line_width = 3, 
        line_dash ="dash", 
        line_color = "grey",
        annotation_text = "Today",
        annotation_position ="top left",
        annotation=dict(font_size=15),
        annotation_font_color = "black"
        
    )
    # Update layout
    fig.update_layout(
        title_text=f"Comprehensive Hotel Griffintown Analytics - {today.date()}",
        title_x=0.5,
        height=1200,
        font_size=10,
        barmode='group',
        plot_bgcolor="#F5F5DC",
        paper_bgcolor= "#FFFFFF"
    )

    # Update y-axis titles and formatting
    fig.update_xaxes(gridcolor='darkgrey', zerolinecolor='black')
    fig.update_yaxes(gridcolor='darkgrey', zerolinecolor='black')
    fig.update_yaxes(title_text="Percentage", row=1, col=1)
    fig.update_yaxes(title_text="Revenue ($)", tickformat='$,.0f', row=1, col=2)
    fig.update_yaxes(title_text="Nights", row=1, col=3)
    fig.update_yaxes(title_text="Count", row=2, col=1)
    fig.update_yaxes(title_text="ADR ($)", tickformat='$,.0f', row=2, col=2)
    fig.update_yaxes(title_text="RevPAR ($)", tickformat='$,.0f', row=2, col=3)
    fig.update_yaxes(title_text="Revenue ($)", tickformat='$,.0f', row=3, col=1)
    fig.update_yaxes(title_text="Days", row=3, col=2)
    fig.update_yaxes(title_text="Days", row=3, col=3)

    # Rotate x-axis labels for better readability
    fig.update_xaxes(tickangle=45)
    fig.show()

def add_line_chart(fig,row, col, y_col, name, year_colors, df_monthly_stats):
    for year in [2024, 2025]:
        faded_color, base_color = year_colors[year]
        
        # Filter data for the specific year
        year_data = df_monthly_stats[df_monthly_stats['Year'] == year].copy()
        today = date.today()
        # Separate data into past and future
        past_data = year_data[year_data['Month'] <= pd.Timestamp(year, today.month, 1)]
        future_data = year_data[year_data['Month'] >= pd.Timestamp(year, today.month, 1)]

        # Add the faded trace for past data
        if not past_data.empty:
            fig.add_trace(
                go.Scatter(
                    x=past_data['MonthName'],
                    y=past_data[y_col],
                    mode="lines+markers",
                    name=f"{name} {year}",
                    line=dict(color=faded_color, width=2),
                    marker=dict(color=faded_color, size=8),
                    showlegend=True
                ),
                row=row, col=col
            )
            
        # Add the bold trace for future data
        if not future_data.empty:
            fig.add_trace(
                go.Scatter(
                    x=future_data['MonthName'],
                    y=future_data[y_col],
                    mode="lines+markers",
                    name=f"{name} {year}",
                    line=dict(color=base_color, width=2),
                    marker=dict(color=base_color, size=8, line=dict(width=2, color=base_color)),
                    showlegend=True
                ),
                row=row, col=col
            )
    
    fig.update_traces(row=row, col=col, textfont_size=12, textposition="top center", cliponaxis=False)

def add_bar_chart(fig,row, col, y_col, name, year_colors, df_monthly_stats):
    for year in [2024, 2025]:
        mask = df_monthly_stats['Year'] == year
        months = df_monthly_stats.loc[mask, 'Month']
        values = df_monthly_stats.loc[mask, y_col]
        faded_color, base_color = year_colors[year]
        today = date.today()
        
        # The month_ts should be compared to the 'today' variable correctly
        marker_colors = [
            faded_color if m < pd.Timestamp(year, today.month, 1) else base_color
            for m in months
        ]
        
        fig.add_trace(
            go.Bar(
                x=df_monthly_stats.loc[mask, 'MonthName'],
                y=values,
                name=f"{name} {year}",
                marker_color=marker_colors,
                opacity=0.9
            ),
            row=row, col=col
        )
    fig.update_traces(row=row,col=col,textfont_size=12, textposition="outside", cliponaxis=False)

    
if(__name__ == "__main__"):
    main()
