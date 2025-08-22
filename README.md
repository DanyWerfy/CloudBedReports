# Cloudbeds API Data Project

This project retrieves data directly from the Cloudbeds server using its API. The extracted data is then used to perform statistical analysis, identify trends, generate insightful graphs, and create various reports.

---

## Features

* **Direct API Access:** Grabs real-time data directly from the Cloudbeds server.
* **Statistical Analysis:** Runs powerful statistical scripts on the collected data.
* **Trend Detection:** Generates reports and visualizations to help identify key trends.
* **Automated Reporting:** Creates different types of reports for easy consumption.

---

## Requirements

To get this project up and running, you'll need to have **Python 3.x** installed on your system. All other necessary libraries are listed in the `requirements.txt` file.

---

## Getting Started

Follow these simple steps to set up the project locally.

### 1. Clone the Repository

First, clone the project from its GitHub repository to your local machine:
`git clone [Your Repository URL]`
`cd [Your Project Folder]`

### 2. Create a Virtual Environment

It's a best practice to use a virtual environment to manage project dependencies. This prevents conflicts with other Python projects on your computer.

`python -m venv .venv`

### 3. Activate the Virtual Environment

Activate the virtual environment you just created.

* **On Windows:**
    `.venv\Scripts\activate`

* **On macOS/Linux:**
    `source .venv/bin/activate`

### 4. Install Dependencies

With the virtual environment active, install all the required packages using `pip`.
`pip install -r requirements.txt`

### 5. API Key Setup

This project requires a Cloudbeds API key to access your data. Create a file named **`.env`** in the root directory of the project. Inside the file, add your API key in the following format:

`CLOUDBEDS_API_KEY="your_api_key_here"`

Replace `"your_api_key_here"` with the actual API key provided by Cloudbeds.

### 6. Run the Scripts

You're ready to start using the project! Run the scripts in the following order to gather data, analyze it, and generate your reports.

#### a. Gather Reservations

This script connects to the Cloudbeds API, retrieves all reservation data, and saves it as a large JSON file in `./data/reservations.json`.

`python ./scripts/gatherReservations.py`

#### b. Run Stats

This script performs various statistical analyses on the reservation data and saves the resulting statistics as a new JSON file in the `./data` folder.

`python ./scripts/runStats.py`

#### c. Generate Graphs

This script creates graphs based on the data. You can specify which type of graph to create: a simple graph for co-owners or a more detailed, comprehensive graph for internal use.

`python ./scripts/generateGraphs.py`
