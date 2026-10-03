# googlemap_webautomation2426

🗺️ Google Maps Web Automation Project

📌 Project Overview

Google Maps Web Automation is a Python-based web automation project developed using Selenium WebDriver. The project automatically opens Google Maps for predefined location pairs, extracts available route information such as distance and travel time, compares multiple routes, captures screenshots, stores the collected data in CSV format, and generates an interactive HTML dashboard for route analysis.

The project eliminates manual Google Maps searching and provides an automated way to collect and analyze route information.

---

🎯 Objectives

- Automate Google Maps route searching.
- Eliminate manual location entry.
- Extract multiple available routes.
- Collect route distance and travel time.
- Convert travel time into minutes for analysis.
- Store route information in CSV format.
- Generate screenshots of Google Maps results.
- Create an attractive HTML report.
- Visualize travel-time data using interactive charts.
- Provide error handling and fallback extraction mechanisms.
- Record timestamps for route data.

---

🛠️ Technologies Used

- Python
- Selenium WebDriver
- Google Maps
- HTML5
- CSS3
- JavaScript
- Chart.js
- CSV
- Regular Expressions (Regex)
- Chrome WebDriver

---

📍 Predefined Location Pairs

The project currently tests three location pairs:

1. Chikkabanavara → Laggere
2. Chikkabanavara → Yeshwanthpur
3. Chikkabanavara → Majestic

The locations can easily be modified in the "LOCATION_PAIRS" section of the Python script.

---

⚙️ Main Features

1. Automatic Google Maps URL Generation

The application dynamically creates Google Maps direction URLs using the source and destination locations.

2. Automated Browser Control

Selenium launches Google Chrome and automatically opens the required Google Maps routes.

3. Multiple Route Extraction

The application attempts to identify individual route cards from the Google Maps page and extracts information from them.

4. Distance Extraction

Regular expressions are used to identify distances such as:

5.2 km
12 km
18.7 km

5. Travel-Time Extraction

The application extracts different time formats, including:

45 min
1 hr
1 hr 20 min
2 hours 15 minutes

6. Time Conversion

Travel time is converted into minutes so that route travel times can be compared and visualized.

For example:

1 hr 30 min → 90 minutes

7. Fallback Extraction

If individual route cards cannot be detected, the application extracts distance and time information from the complete page text.

This makes the extraction process more tolerant of changes in the Google Maps page structure.

8. Screenshot Generation

A screenshot of the Google Maps result is automatically captured and stored for each location pair.

Example:

google_maps_results/
├── route_1.png
├── route_2.png
└── route_3.png

9. CSV Data Storage

The extracted information is stored in:

route_history.csv

The CSV contains:

- Timestamp
- From location
- To location
- Route
- Distance
- Travel Time

10. Interactive HTML Dashboard

The project generates:

route_report.html

The dashboard displays:

- Total location pairs
- Total routes extracted
- Route details
- Distance
- Travel time
- Timestamp
- Interactive charts

11. Data Visualization

The HTML report uses Chart.js to visualize travel-time data.

Available chart types include:

- 📊 Bar Chart
- 📈 Line Chart
- 🥧 Pie Chart

The user can select the required chart type from a dropdown menu.

12. Error Handling

The project uses "try-except" blocks to handle problems such as:

- Route elements not being found
- Extraction failures
- Screenshot errors
- Page-element changes
- Unexpected Selenium errors

---

📂 Project Structure

Google-Maps-Web-Automation/
│
├── google_maps_automation.py
│
└── google_maps_results/
    │
    ├── route_1.png
    ├── route_2.png
    ├── route_3.png
    ├── route_history.csv
    └── route_report.html

---

🔄 Project Workflow

Start
  ↓
Define Location Pairs
  ↓
Launch Chrome using Selenium
  ↓
Create Google Maps Route URL
  ↓
Open Google Maps
  ↓
Wait for Route Information
  ↓
Extract Multiple Routes
  ↓
Extract Distance & Travel Time
  ↓
Convert Travel Time to Minutes
  ↓
Capture Screenshot
  ↓
Store Data in CSV
  ↓
Generate HTML Dashboard
  ↓
Display Interactive Charts
  ↓
End

---

▶️ How to Run

Step 1: Install Python

Make sure Python is installed on the system.

Check using:

python --version

Step 2: Install Selenium

pip install selenium

Step 3: Make sure Google Chrome is installed

The project uses Chrome with Selenium WebDriver.

Step 4: Run the Python script

python google_maps_automation.py

Step 5: View the generated report

After execution, open:

google_maps_results/route_report.html

The report contains the extracted route information and interactive travel-time charts.

---

📊 Sample Output

From| To| Route| Distance| Travel Time
Chikkabanavara| Laggere| Route 1| 8.2 km| 25 min
Chikkabanavara| Laggere| Route 2| 9.5 km| 30 min
Chikkabanavara| Yeshwanthpur| Route 1| 7.8 km| 24 min

The actual values depend on the Google Maps results available when the automation is executed.

---

🔐 Important Note

Google Maps is a dynamic website, so its HTML structure and CSS selectors can change over time. Therefore, Selenium selectors used for route extraction may require updates if Google Maps changes its page structure.

The project includes fallback page-text extraction to improve robustness.

---

🚀 Future Enhancements

Possible improvements include:

- Automatic route comparison based on shortest distance or travel time.
- Traffic-aware route analysis.
- Export reports to PDF.
- Email notification with route reports.
- Scheduled automatic route collection.
- Database storage instead of CSV.
- Support for user-entered locations.
- Historical travel-time analysis.
- Additional charts such as distance comparison.
- Headless browser execution.
- Automated testing of extracted data.

---

👩‍💻 Project Outcome

This project demonstrates practical knowledge of Python automation, Selenium WebDriver, web scraping techniques, regular expressions, file handling, CSV processing, HTML/CSS/JavaScript, data visualization, error handling, and automated reporting.

It provides an end-to-end automation workflow starting from Google Maps route generation and ending with a structured, visual route-analysis dashboard.
