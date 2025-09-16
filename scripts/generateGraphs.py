
# general imports
import os
import json
import webbrowser
import pandas as pd

# date imports
from calendar import month_name
from datetime import date, datetime

# graph imports
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

years = [2024, 2025]
year_colors = {
    years[0]: ("#5F768E", "#B0C4DE"),
    years[1]: ("#D4610E", "#D2B48C")
}


def main():
    jsonFilePath = "../data/09-16-2025_4_months.json"
    with open(jsonFilePath, "r", encoding="utf-8") as f:
        monthlyStats = json.load(f)
    createGraph(monthlyStats=monthlyStats)


# this function creates a standard graph that can be distributed to co-owners or others
def createGraph(monthlyStats):
    # where to save the HTML
    outputPath = "../data/stats.html"

    # initlize the graphs and convert monthly stats into a format to be worked with
    fig, df_monthly_stats = initFigure(monthlyStats=monthlyStats)

    # Add the first chart: Occupancy Percentage
    add_bar_chart(fig, 2, 1, 'occupancyPercent', 'Occupancy %', year_colors, df_monthly_stats)

    # add the table for the occupancy percent
    add_table(fig,3,1, "occupancyPercent", year_colors, df_monthly_stats)

    # Add the second chart: Number of Reservations
    add_bar_chart(fig, 4, 1, 'nightsRented', 'Reservation Nights', year_colors, df_monthly_stats)

    # add annotations to the figure. Annotations are the legends, descriptions, and include the title too
    addAnnotations(fig)

    # update layout information
    updateLayout(fig)

    saveAndViewFig(fig,outputPath=outputPath)


    # this function creates a more comprehensive graph
    # this should be used only for internal use


# this function creates a more comprehensive graph to be viewed internally.
# note this function is not as organized as createGraph is
def createComprehensiveGraph(monthlyStats):
    # Convert the dictionary to a Pandas DataFrame
    df_monthly_stats = pd.DataFrame.from_dict(monthlyStats, orient='index')
    df_monthly_stats.index.name = 'Month'
    df_monthly_stats.reset_index(inplace=True)

    # Parse month to datetime and extract year, month name
    df_monthly_stats['Month'] = pd.to_datetime(df_monthly_stats['Month'])
    df_monthly_stats['Year'] = df_monthly_stats['Month'].dt.year
    df_monthly_stats['MonthName'] = df_monthly_stats['Month'].dt.strftime('%b')

    today = date.today() 

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


# helper function to initialize a figure
def initFigure(monthlyStats):
    # the num rows is te number of graphs to display - 2.
# the extra 2 are at the top and bottom to allow for extra spacing
    numRows = 5
    # the height of each respecive row
    rowHeights = [.1, 0.3, 0.1,0.4,0.1]
    # spacing between each row
    vertSpacing = .1
    df_monthly_stats = pd.DataFrame.from_dict(monthlyStats, orient='index')
    df_monthly_stats.index.name = 'Month'
    df_monthly_stats.reset_index(inplace=True)

    # Convert the 'Month' string to a datetime object and extract year and month name
    df_monthly_stats['Month'] = pd.to_datetime(df_monthly_stats['Month'])
    df_monthly_stats['Year'] = df_monthly_stats['Month'].dt.year
    df_monthly_stats['MonthName'] = df_monthly_stats['Month'].dt.strftime('%b')
    fig = make_subplots(
        rows=numRows, cols=1,
        shared_xaxes=False,
        vertical_spacing=vertSpacing,
        # domain is for the table, xy for everything else
        specs=[[{"type": "xy"}], [{"type": "xy"}], [{"type": "domain"}], [{"type": "xy"}], [{"type": "xy"}]],
        # titles for the charts
        subplot_titles=(
            "",
            f"Occupancy (%)", 
            f"Occupancy (%) Table", 
            f"Number Of Reservations"
        ),
        row_heights = rowHeights,
    )
    return (fig, df_monthly_stats)


# helper function to save the fig and view the HTML in default browser
def saveAndViewFig(fig, outputPath):
    fig.write_html(outputPath)
    absolute_path = os.path.abspath(outputPath)
    # open the HTML in default browser
    webbrowser.open_new_tab(f"file://{absolute_path}")

# helper function to update the layout. This is used for the simple graph 
def updateLayout(fig):
    chartHeights = 2500
    fig.update_layout(
    title=go.layout.Title(
        text=f"Werfy Luxury Apart-Hotel - {years[0]}/{years[1]} Analytics<br><sup>These analytics are generated on {date.today().strftime("%Y-%m-%d")}</sup>" ,
        xref="paper",
        x=0.5,
        xanchor="center",
        yanchor="top"
    ),
    title_x=0.5,
    height=chartHeights,
    plot_bgcolor="#F5F5DC",
    paper_bgcolor="#DBE8FF",
    showlegend=False,
    )

    # Update y-axis titles for each subplot
    fig.update_yaxes(title_text="Occupancy Percentage (%)", row=1, col=1)
    fig.update_yaxes(title_text="Occupancy Percentage (%)", row=2, col=1)

    fig.update_yaxes(title_text="Number of Reservation Nights", row=3, col=1)
    fig.update_xaxes(showgrid=False) 
# helper function to create a line chart
def add_line_chart(fig,row, col, y_col, name, year_colors, df_monthly_stats):
    for year in years:
        faded_color, base_color = year_colors[year]
        
        # Filter data for the specific year
        year_data = df_monthly_stats[df_monthly_stats['Year'] == year].copy()
        today = date.today()
        # Separate data into past and future
        past_data = year_data[year_data['Month'] <= pd.Timestamp(year, today.month, 1)]
        future_data = year_data[year_data['Month'] >= pd.Timestamp(year, today.month, 1)]

        # Add the faded trace for past data
        
        if not past_data.empty:
            past_data.loc[y_col] = past_data[y_col].round(0)
            fig.add_trace(
                go.Scatter(
                    x=past_data['MonthName'],
                    y=past_data[y_col],
                    mode="lines+markers",
                    name=f"{name} {year}",
                    line=dict(color=faded_color, width=2),
                    marker=dict(color=faded_color, size=8),
                    # showlegend=True,
                    
                ),
                row=row, col=col
            )
            
        # Add the bold trace for future data
        if not future_data.empty:
            future_data[y_col] = future_data[y_col]
            fig.add_trace(
                go.Scatter(
                    x=future_data['MonthName'],
                    y=future_data[y_col],
                    mode="lines+markers",
                    name=f"{name} {year}",
                    line=dict(color=base_color, width=2),
                    marker=dict(color=base_color, size=8, line=dict(width=2, color=base_color)),
                    # showlegend=True

                ),
                row=row, col=col
            )
    
    fig.update_traces(row=row, col=col, textfont_size=12, textposition="top center", cliponaxis=False)

# helper function to create a bar chart
def add_bar_chart(fig,row, col, y_col, name, year_colors, df_monthly_stats):
    for year in years:
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
        values = values.round(0) 
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

# helper function to add a table
def add_table(fig, row, col, y_col, year_colors, df_monthly_stats):
    df_monthly_stats['year'] = df_monthly_stats.Month.dt.year
    df_monthly_stats['month_name'] = df_monthly_stats.Month.dt.strftime('%B')
    ordered_months = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    df_monthly_stats['month_name'] = pd.Categorical(df_monthly_stats['month_name'], categories=ordered_months, ordered=True)
    df_pivoted = df_monthly_stats.pivot(index='year', columns='month_name', values=y_col).reset_index()
    months_columns = [col for col in df_pivoted.columns if col in ordered_months]
    for col_name in months_columns:
        df_pivoted[col_name] = df_pivoted[col_name].round(0)
    header_values = ['Year'] + months_columns
    cell_values = [df_pivoted['year']] + [df_pivoted[month] for month in months_columns]

    row_colors = []
    for year in df_pivoted['year']:
        if year in year_colors:
            row_colors.append(year_colors[year][1])  # Use the faded color
        else:
            row_colors.append('rgba(242, 242, 242, 1)') # Default color if year not found

    fill_colors = [row_colors] * len(months_columns)

    fig.add_trace(
        go.Table(
            header=dict(values=header_values),
            cells=dict(
                values=cell_values,
                fill_color=fill_colors,
            )
        ),
        row=row, col=col
    )

# function to create annotations on the page
# used for descriptions and legends

def addAnnotations(fig):
    # 0 is the bold color
    colorYr1 = year_colors[years[0]][0]
    colorYr2 = year_colors[years[1]][0]
    legend = f"<span style='color:{colorYr1};'>&#9632;</span> {years[0]} | <span style='color:{colorYr2};'>&#9632;</span> {years[1]}<br><br>"
    descriptions = [
    f"{legend}This chart displays the monthly occupancy rates. For future months, beginning in September, the data is less accurate. <br> This is because more reservations are typically made closer to the final date, meaning the data is not yet complete and is subject to change as more bookings are secured.",
    f"This table provides a detailed, year-over-year comparison of occupancy rates for each month.  <br> The information for upcoming months, starting in September, should be considered preliminary and less accurate. <br> As more reservations are made closer to the final date, this data is not yet complete and is expected to change.",
    f"{legend}This chart shows the number of reservation nights per month. This is a metric which shows how many nights have been booked. It is important to note that the data for future months, beginning in September, is less accurate.<br> Since more reservations are made closer to the final date, the data is not yet complete and does not include bookings that may be made in the coming weeks and months.",
    f"{legend}This chart shows the average length of a guest's stay.The data for future months, beginning in September, is less accurate.<br>  This is because more reservations are made closer to the final date, meaning the data is not yet complete and is expected to change as more bookings are finalized.",
    f"This dashboard provides a comprehensive overview of {years[1]}'s performance compared to {years[0]}.<br> The information for upcoming months, beginning in September, is preliminary and less accurate.<br> This is because most reservations are made closer to the final date, meaning the data is not yet complete and is subject to change as more bookings are secured."
    ]
    # grab all current annotations (titles)
    annotations = list(fig.layout.annotations)
    annotations.append(go.layout.Annotation(
        text=descriptions[0],
        showarrow=False,
        xref="paper",
        yref="paper",
        # ew shitty positioning.
        # this is based off trial and error. the numbers are out of 1, 1 being at the top 0 being the bottom 
        x=0.5,
        y=.65,
        xanchor="center",
        yanchor="top",
        font=dict(size=15)
    ))
    annotations.append(go.layout.Annotation(
        text=descriptions[1],
        showarrow=False,
        xref="paper",
        yref="paper",
        x=0.5,
        y=.50,
        xanchor="center",
        yanchor="top",
        font=dict(size=15)
    ))
    annotations.append(go.layout.Annotation(
        text=descriptions[2],
        showarrow=False,
        xref="paper",
        yref="paper",
        x=0.5,
        y=.14,
        xanchor="center",
        yanchor="top",
        font=dict(size=15)
    ))
    annotations.append(go.layout.Annotation(
        text=descriptions[4],
        showarrow=False,
        xref="paper",
        yref="paper",
        x=0.5,
        y=.97,
        xanchor="center",
        yanchor="top",
        font=dict(size=15) 
    ))
    fig.update_layout(annotations=annotations)


if __name__ == "__main__":
    main()