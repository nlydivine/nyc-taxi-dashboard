# NYC Taxi Dashboard

A dashboard for exploring and analyzing NYC Taxi trip data. The project combines data processing, database management, backend APIs, and data visualization to provide insights into taxi trips across New York City.

## Team Members

* Nshuti Lydivine
* Sangwa Lina Tiffany
* Admire Chagaserango

## Technologies Used

* Python
* Flask
* PostgreSQL / SQLite
* Pandas
* HTML, CSS, JavaScript
* Docker
* Git & GitHub

## Project Structure

```text
nyc-taxi-dashboard/
├── api/
├── database/
├── frontend/
├── data/
└── README.md
```

## Setup

Clone the repository:

```bash
git clone https://github.com/nlydivine/nyc-taxi-dashboard.git
cd nyc-taxi-dashboard
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Load the database:

```bash
python database/insert_zones.py
python database/insert_trips.py
```

Run the API:

```bash
python api/server.py
```

## Features

* Store taxi trip data in a relational database
* Query trip information through a Flask API
* Analyze pickup and dropoff patterns
* Visualize trends and statistics

## Team Participation Sheet Link

https://docs.google.com/spreadsheets/d/1qxBGiE-POxkCGxn0fO9SizrMUbAoaF0W0e4it4_ZWxU/edit?usp=sharing


