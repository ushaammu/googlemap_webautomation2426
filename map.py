from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from urllib.parse import quote
from datetime import datetime

import csv
import os
import re
import time
import json


LOCATION_PAIRS = [

    {
        "from": "Chikkabanavara, Bangalore",
        "to": "Laggere, Bangalore"
    },

    {
        "from": "Chikkabanavara, Bangalore",
        "to": "Yeshwanthpur, Bangalore"
    },

    {
        "from": "Chikkabanavara, Bangalore",
        "to": "Majestic, Bangalore"
    }

]


# PROJECT SETTINGS


PAGE_WAIT = 30

BROWSER_CLOSE_DELAY = 3

OUTPUT_FOLDER = "google_maps_results"

os.makedirs(
    OUTPUT_FOLDER,
    exist_ok=True
)


# START CHROME

options = webdriver.ChromeOptions()

options.add_argument("--start-maximized")

driver = webdriver.Chrome(
    options=options
)

wait = WebDriverWait(
    driver,
    PAGE_WAIT
)


# CREATE GOOGLE MAPS URL

def create_maps_url(
    from_location,
    to_location
):

    source = quote(
        from_location
    )

    destination = quote(
        to_location
    )

    return (
        "https://www.google.com/maps/dir/"
        + source
        + "/"
        + destination
    )

# EXTRACT DISTANCE
def extract_distance(text):

    match = re.search(
        r"\b\d+(?:\.\d+)?\s*km\b",
        text,
        re.IGNORECASE
    )

    if match:

        return match.group(0)

    return "Not found"



# EXTRACT TIME


def extract_time(text):

    patterns = [

        r"\b\d+\s*hr\s*\d+\s*min\b",

        r"\b\d+\s*hrs\s*\d+\s*mins\b",

        r"\b\d+\s*hour[s]?\s*\d+\s*minute[s]?\b",

        r"\b\d+\s*hr[s]?\b",

        r"\b\d+\s*hour[s]?\b",

        r"\b\d+\s*min[s]?\b",

        r"\b\d+\s*minute[s]?\b"

    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            return match.group(0)

    return "Not found"

# CONVERT TIME TO MINUTES


def time_to_minutes(
    time_text
):

    text = time_text.lower()

    hours = 0
    minutes = 0

    hour_match = re.search(
        r"(\d+)\s*(?:hr|hrs|hour|hours)",
        text
    )

    minute_match = re.search(
        r"(\d+)\s*(?:min|mins|minute|minutes)",
        text
    )

    if hour_match:

        hours = int(
            hour_match.group(1)
        )

    if minute_match:

        minutes = int(
            minute_match.group(1)
        )

    return (
        hours * 60
        + minutes
    )


# EXTRACT MULTIPLE ROUTES


def extract_multiple_routes():

    print(
        "Searching for individual routes..."
    )

    time.sleep(5)

    routes = []


    # GOOGLE MAPS ROUTE SELECTORS
    

    selectors = [

        "div.Nv2PK",

        "div[data-trip-index]",

        "[jsaction*='directions']",

        "div.MjjYud"

    ]

    route_elements = []


    # FIND ROUTE CARDS
   
    for selector in selectors:

        try:

            elements = driver.find_elements(
                By.CSS_SELECTOR,
                selector
            )

            valid_elements = []

            for element in elements:

                try:

                    text = element.text.strip()

                    has_distance = re.search(
                        r"\d+(?:\.\d+)?\s*km",
                        text,
                        re.IGNORECASE
                    )

                    has_time = re.search(
                        r"\d+\s*"
                        r"(?:min|mins|minute|minutes|"
                        r"hr|hrs|hour|hours)",
                        text,
                        re.IGNORECASE
                    )

                    if (
                        has_distance
                        and
                        has_time
                    ):

                        valid_elements.append(
                            element
                        )

                except Exception:

                    continue

            if valid_elements:

                route_elements = valid_elements

                print(
                    "Possible route cards found:",
                    len(route_elements)
                )

                break

        except Exception:

            continue

    # --------------------------------------------------------
    # EXTRACT ROUTES
    # --------------------------------------------------------

    for index, element in enumerate(
        route_elements,
        start=1
    ):

        try:

            text = element.text.strip()

            distance = extract_distance(
                text
            )

            travel_time = extract_time(
                text
            )

            if (
                distance != "Not found"
                or
                travel_time != "Not found"
            ):

                routes.append(
                    {
                        "route":
                        f"Route {index}",

                        "distance":
                        distance,

                        "time":
                        travel_time
                    }
                )

        except Exception:

            continue

    # --------------------------------------------------------
    # FALLBACK PAGE TEXT EXTRACTION
    # --------------------------------------------------------

    if not routes:

        print(
            "Individual route cards not detected."
        )

        print(
            "Using page-text extraction..."
        )

        try:

            body = driver.find_element(
                By.TAG_NAME,
                "body"
            )

            page_text = body.text

            distances = re.findall(
                r"\b\d+(?:\.\d+)?\s*km\b",
                page_text,
                re.IGNORECASE
            )

            times = re.findall(
                r"\b\d+\s*"
                r"(?:hr|hrs|hour|hours|min|mins|"
                r"minute|minutes)"
                r"(?:\s+\d+\s*"
                r"(?:min|mins|minute|minutes))?",
                page_text,
                re.IGNORECASE
            )

            distances = list(
                dict.fromkeys(
                    distances
                )
            )

            times = list(
                dict.fromkeys(
                    times
                )
            )

            count = min(
                len(distances),
                len(times)
            )

            for i in range(count):

                routes.append(
                    {
                        "route":
                        f"Route {i + 1}",

                        "distance":
                        distances[i],

                        "time":
                        times[i]
                    }
                )

        except Exception as e:

            print(
                "Fallback extraction error:",
                e
            )

    return routes


# ============================================================
# SCREENSHOT
# ============================================================

def save_screenshot(
    pair_number
):

    filename = (
        f"route_{pair_number}.png"
    )

    path = os.path.join(
        OUTPUT_FOLDER,
        filename
    )

    try:

        driver.save_screenshot(
            path
        )

        print(
            "Screenshot saved:",
            path
        )

    except Exception as e:

        print(
            "Screenshot error:",
            e
        )


# ============================================================
# SAVE CSV
# ============================================================

def save_csv(
    all_results
):

    path = os.path.join(
        OUTPUT_FOLDER,
        "route_history.csv"
    )

    with open(
        path,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(
            file
        )

        writer.writerow(
            [
                "Timestamp",
                "From",
                "To",
                "Route",
                "Distance",
                "Travel Time"
            ]
        )

        for result in all_results:

            writer.writerow(
                [
                    result["timestamp"],
                    result["from"],
                    result["to"],
                    result["route"],
                    result["distance"],
                    result["time"]
                ]
            )

    print(
        "CSV saved:",
        path
    )


# ============================================================
# CREATE HTML REPORT
# ============================================================

def create_html_report(
    all_results
):

    path = os.path.join(
        OUTPUT_FOLDER,
        "route_report.html"
    )

    # --------------------------------------------------------
    # TABLE ROWS
    # --------------------------------------------------------

    rows = ""

    for result in all_results:

        minutes = time_to_minutes(
            result["time"]
        )

        rows += f"""
        <tr>

            <td>{result["from"]}</td>

            <td>{result["to"]}</td>

            <td>
                <span class="route-badge">
                    {result["route"]}
                </span>
            </td>

            <td>
                <strong>
                    {result["distance"]}
                </strong>
            </td>

            <td>
                <strong>
                    {result["time"]}
                </strong>
            </td>

            <td>
                {result["timestamp"]}
            </td>

        </tr>
        """

    # --------------------------------------------------------
    # CHART DATA
    # --------------------------------------------------------

    chart_labels = []
    chart_values = []

    for index, result in enumerate(
        all_results
    ):

        minutes = time_to_minutes(
            result["time"]
        )

        if minutes > 0:

            label = (
                result["route"]
                + " - "
                + result["to"]
            )

            chart_labels.append(
                label
            )

            chart_values.append(
                minutes
            )

    labels_json = json.dumps(
        chart_labels
    )

    values_json = json.dumps(
        chart_values
    )

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    total_pairs = len(
        LOCATION_PAIRS
    )

    total_routes = len(
        all_results
    )

    generated_time = datetime.now().strftime(
        "%d-%m-%Y %H:%M"
    )

    # --------------------------------------------------------
    # HTML
    # --------------------------------------------------------

    html = f"""
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width, initial-scale=1.0">

<title>
Google Maps Web Automation Dashboard
</title>


<!-- Chart.js -->

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>


<style>

* {{
    box-sizing: border-box;
}}

body {{

    margin: 0;

    font-family:
        "Segoe UI",
        Arial,
        sans-serif;

    background:
        linear-gradient(
            135deg,
            #eef2ff,
            #f8fafc,
            #ecfeff
        );

    color: #1e293b;

}}


.header {{

    background:
        linear-gradient(
            135deg,
            #2563eb,
            #4f46e5,
            #7c3aed
        );

    color: white;

    padding: 45px 30px;

    text-align: center;

    box-shadow:
        0 8px 25px
        rgba(37, 99, 235, 0.25);

}}


.header h1 {{

    margin: 0;

    font-size: 34px;

    letter-spacing: 0.5px;

}}


.header p {{

    margin-top: 10px;

    opacity: 0.9;

    font-size: 16px;

}}


.container {{

    max-width: 1250px;

    margin: 35px auto;

    padding: 0 20px;

}}


.cards {{

    display: grid;

    grid-template-columns:
        repeat(
            auto-fit,
            minmax(220px, 1fr)
        );

    gap: 20px;

    margin-bottom: 30px;

}}


.card {{

    background: white;

    padding: 25px;

    border-radius: 18px;

    box-shadow:
        0 8px 25px
        rgba(15, 23, 42, 0.08);

    border-left:
        6px solid #4f46e5;

    transition: 0.25s;

}}


.card:hover {{

    transform:
        translateY(-4px);

    box-shadow:
        0 12px 30px
        rgba(15, 23, 42, 0.14);

}}


.card-icon {{

    font-size: 30px;

}}


.card-title {{

    color: #64748b;

    font-size: 14px;

    margin-top: 8px;

}}


.card-value {{

    font-size: 27px;

    font-weight: 700;

    color: #1e293b;

    margin-top: 5px;

}}


.section {{

    background: white;

    padding: 30px;

    border-radius: 18px;

    margin-bottom: 30px;

    box-shadow:
        0 8px 25px
        rgba(15, 23, 42, 0.08);

}}


.section h2 {{

    margin-top: 0;

    color: #312e81;

}}


.table-container {{

    overflow-x: auto;

}}


table {{

    width: 100%;

    border-collapse: collapse;

    min-width: 900px;

}}


th {{

    background:
        linear-gradient(
            135deg,
            #4f46e5,
            #2563eb
        );

    color: white;

    padding: 14px;

    text-align: center;

    font-size: 14px;

}}


td {{

    padding: 13px;

    border-bottom:
        1px solid #e2e8f0;

    text-align: center;

    font-size: 14px;

}}


tr:hover td {{

    background: #f8fafc;

}}


.route-badge {{

    background: #ede9fe;

    color: #6d28d9;

    padding: 6px 12px;

    border-radius: 20px;

    font-weight: 600;

}}


.chart-controls {{

    display: flex;

    align-items: center;

    gap: 15px;

    flex-wrap: wrap;

    margin-bottom: 25px;

}}


.chart-controls label {{

    font-weight: 700;

    color: #334155;

}}


#chartType {{

    padding: 11px 16px;

    border-radius: 10px;

    border:
        2px solid #6366f1;

    background: white;

    color: #312e81;

    font-size: 15px;

    font-weight: 600;

    cursor: pointer;

    outline: none;

}}


#chartType:hover {{

    background: #eef2ff;

}}


.chart-wrapper {{

    position: relative;

    width: 100%;

    height: 450px;

}}


.info-box {{

    background:
        linear-gradient(
            135deg,
            #eff6ff,
            #eef2ff
        );

    border-left:
        5px solid #2563eb;

    padding: 15px;

    border-radius: 10px;

    margin-bottom: 20px;

    color: #334155;

}}


.footer {{

    text-align: center;

    padding: 30px;

    color: #64748b;

    font-size: 14px;

}}


@media(max-width: 700px) {{

    .header h1 {{

        font-size: 25px;

    }}

    .chart-wrapper {{

        height: 350px;

    }}

}}

</style>

</head>


<body>


<!-- ===================================================== -->
<!-- HEADER -->
<!-- ===================================================== -->

<div class="header">

    <h1>
        🗺️ Google Maps Web Automation
    </h1>

    <p>
        Automated Route Extraction & Travel Analysis
    </p>

</div>


<div class="container">


<!-- ===================================================== -->
<!-- SUMMARY CARDS -->
<!-- ===================================================== -->

<div class="cards">


    <div class="card">

        <div class="card-icon">
            📍
        </div>

        <div class="card-title">
            Location Pairs
        </div>

        <div class="card-value">
            {total_pairs}
        </div>

    </div>


    <div class="card">

        <div class="card-icon">
            🛣️
        </div>

        <div class="card-title">
            Routes Extracted
        </div>

        <div class="card-value">
            {total_routes}
        </div>

    </div>


    <div class="card">

        <div class="card-icon">
            📊
        </div>

        <div class="card-title">
            Chart
        </div>

        <div class="card-value">
            Interactive
        </div>

    </div>


    <div class="card">

        <div class="card-icon">
            ⏱️
        </div>

        <div class="card-title">
            Generated
        </div>

        <div class="card-value"
             style="font-size:18px;">

            {generated_time}

        </div>

    </div>


</div>


<!-- ===================================================== -->
<!-- ROUTE DETAILS -->
<!-- ===================================================== -->

<div class="section">

    <h2>
        📋 Route Details
    </h2>

    <div class="table-container">

        <table>

            <thead>

                <tr>

                    <th>From</th>

                    <th>To</th>

                    <th>Route</th>

                    <th>Distance</th>

                    <th>Travel Time</th>

                    <th>Timestamp</th>

                </tr>

            </thead>

            <tbody>

                {rows}

            </tbody>

        </table>

    </div>

</div>


<!-- ===================================================== -->
<!-- INTERACTIVE CHART -->
<!-- ===================================================== -->

<div class="section">

    <h2>
        📊 Travel Time Analysis
    </h2>


    <div class="info-box">

        Select a chart type below.
        The same chart will update automatically.

    </div>


    <div class="chart-controls">

        <label for="chartType">
            Choose Chart Type:
        </label>


        <select
            id="chartType"
            onchange="changeChartType()"
        >

            <option value="bar">
                📊 Bar Chart
            </option>

            <option value="line">
                📈 Line Chart
            </option>

            <option value="pie">
                🥧 Pie Chart
            </option>

        </select>

    </div>


    <div class="chart-wrapper">

        <canvas
            id="travelChart"
        ></canvas>

    </div>

</div>


</div>


<!-- ===================================================== -->
<!-- FOOTER -->
<!-- ===================================================== -->

<div class="footer">

    Google Maps Web Automation Project

    <br>

    Generated automatically using
    Python + Selenium + Chart.js

</div>


<!-- ===================================================== -->
<!-- JAVASCRIPT CHART -->
<!-- ===================================================== -->

<script>

const labels = {labels_json};

const values = {values_json};

let chart;


function getColors(count) {{

    const colors = [

        "#2563eb",
        "#7c3aed",
        "#db2777",
        "#ea580c",
        "#16a34a",
        "#0891b2",
        "#ca8a04",
        "#4f46e5",
        "#9333ea",
        "#0284c7"

    ];

    const result = [];

    for (
        let i = 0;
        i < count;
        i++
    ) {{

        result.push(
            colors[
                i % colors.length
            ]
        );

    }}

    return result;

}}


function createChart(type) {{

    const canvas =
        document.getElementById(
            "travelChart"
        );

    const ctx =
        canvas.getContext("2d");


    if (chart) {{

        chart.destroy();

    }}


    let chartType = type;


    // ------------------------------------------------------
    // PIE CHART
    // ------------------------------------------------------

    if (type === "pie") {{

        chart = new Chart(
            ctx,
            {{

                type: "pie",

                data: {{

                    labels: labels,

                    datasets: [{{

                        label:
                            "Travel Time",

                        data: values,

                        backgroundColor:
                            getColors(
                                values.length
                            ),

                        borderColor:
                            "#ffffff",

                        borderWidth: 2

                    }}]

                }},

                options: {{

                    responsive: true,

                    maintainAspectRatio: false,

                    plugins: {{

                        legend: {{

                            position: "right"

                        }},

                        title: {{

                            display: true,

                            text:
                                "Travel Time by Route"

                        }}

                    }}

                }}

            }}

        );

        return;

    }}


    // ------------------------------------------------------
    // BAR / LINE
    // ------------------------------------------------------

    chart = new Chart(
        ctx,
        {{

            type: chartType,

            data: {{

                labels: labels,

                datasets: [{{

                    label:
                        "Travel Time (minutes)",

                    data: values,

                    backgroundColor:
                        type === "line"
                        ? "rgba(37, 99, 235, 0.20)"
                        : getColors(
                            values.length
                        ),

                    borderColor:
                        "#2563eb",

                    borderWidth: 2,

                    fill:
                        type === "line",

                    tension:
                        0.35

                }}]

            }},

            options: {{

                responsive: true,

                maintainAspectRatio: false,

                scales: {{

                    y: {{

                        beginAtZero: true,

                        title: {{

                            display: true,

                            text:
                                "Travel Time (minutes)"

                        }}

                    }},

                    x: {{

                        title: {{

                            display: true,

                            text:
                                "Routes"

                        }}

                    }}

                }},

                plugins: {{

                    legend: {{

                        display: true

                    }},

                    title: {{

                        display: true,

                        text:
                            "Google Maps Travel Time Comparison"

                    }}

                }}

            }}

        }}

    );

}}


// ----------------------------------------------------------
// CHANGE CHART
// ----------------------------------------------------------

function changeChartType() {{

    const selected =
        document.getElementById(
            "chartType"
        ).value;

    createChart(
        selected
    );

}}


// ----------------------------------------------------------
// INITIAL CHART
// ----------------------------------------------------------

createChart(
    "bar"
);

</script>


</body>

</html>
"""

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            html
        )

    print(
        "HTML report saved:",
        path
    )


# ============================================================
# DISPLAY RESULTS
# ============================================================

def display_results(
    from_location,
    to_location,
    routes
):

    print()

    print("=" * 70)

    print(
        "GOOGLE MAPS ROUTE RESULT"
    )

    print("=" * 70)

    print()

    print(
        "FROM:",
        from_location
    )

    print(
        "TO:",
        to_location
    )

    print()

    print(
        "Routes found:",
        len(routes)
    )

    print("-" * 70)

    for route in routes:

        print()

        print(
            route["route"]
        )

        print(
            "Distance    :",
            route["distance"]
        )

        print(
            "Travel Time :",
            route["time"]
        )

        print("-" * 70)


# ============================================================
# MAIN PROGRAM
# ============================================================

all_results = []


try:

    print()

    print("=" * 70)

    print(
        "     GOOGLE MAPS WEB AUTOMATION PROJECT"
    )

    print("=" * 70)

    print()

    # ========================================================
    # PROCESS 3 LOCATION PAIRS
    # ========================================================

    for pair_number, pair in enumerate(
        LOCATION_PAIRS,
        start=1
    ):

        from_location = pair[
            "from"
        ]

        to_location = pair[
            "to"
        ]

        print()

        print("=" * 70)

        print(
            f"LOCATION PAIR {pair_number} / "
            f"{len(LOCATION_PAIRS)}"
        )

        print("=" * 70)

        print(
            "From:",
            from_location
        )

        print(
            "To:",
            to_location
        )

        # ----------------------------------------------------
        # CREATE URL
        # ----------------------------------------------------

        url = create_maps_url(
            from_location,
            to_location
        )

        print()

        print(
            "Opening Google Maps..."
        )

        # ----------------------------------------------------
        # OPEN GOOGLE MAPS
        # ----------------------------------------------------

        driver.get(
            url
        )

        wait.until(
            EC.presence_of_element_located(
                (
                    By.TAG_NAME,
                    "body"
                )
            )
        )

        time.sleep(8)

        print(
            "Google Maps loaded."
        )

        # ----------------------------------------------------
        # EXTRACT ROUTES
        # ----------------------------------------------------

        routes = extract_multiple_routes()

        # ----------------------------------------------------
        # DISPLAY
        # ----------------------------------------------------

        display_results(
            from_location,
            to_location,
            routes
        )

        # ----------------------------------------------------
        # TIMESTAMP
        # ----------------------------------------------------

        timestamp = datetime.now().strftime(
            "%d-%m-%Y %H:%M:%S"
        )

        # ----------------------------------------------------
        # STORE RESULTS
        # ----------------------------------------------------

        for route in routes:

            all_results.append(
                {
                    "timestamp":
                    timestamp,

                    "from":
                    from_location,

                    "to":
                    to_location,

                    "route":
                    route["route"],

                    "distance":
                    route["distance"],

                    "time":
                    route["time"]
                }
            )

        
        # SCREENSHOT
      

        save_screenshot(
            pair_number
        )

    # SAVE CSV
    

    print()

    print(
        "Saving CSV..."
    )

    save_csv(
        all_results
    )

    # ========================================================
    # CREATE HTML REPORT
    # ========================================================

    print(
        "Creating interactive HTML report..."
    )

    create_html_report(
        all_results
    )

    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print()

    print("=" * 70)

    print(
        "AUTOMATION COMPLETED SUCCESSFULLY"
    )

    print("=" * 70)

    print()

    print(
        "Location pairs processed:",
        len(LOCATION_PAIRS)
    )

    print(
        "Total routes extracted:",
        len(all_results)
    )

    print()

    print(
        "Results folder:"
    )

    print(
        os.path.abspath(
            OUTPUT_FOLDER
        )
    )

    print()

    print(
        "Generated files:"
    )

    print(
        "1. route_history.csv"
    )

    print(
        "2. route_report.html"
    )

    print(
        "3. route_1.png"
    )

    print(
        "4. route_2.png"
    )

    print(
        "5. route_3.png"
    )

    print()

    print(
        "Open route_report.html in Chrome."
    )

    print(
        "Use the Chart Type dropdown "
        "inside the report."
    )

    print()

    print(
        f"Chrome will close in "
        f"{BROWSER_CLOSE_DELAY} seconds..."
    )

    time.sleep(
        BROWSER_CLOSE_DELAY
    )


except Exception as e:

    print()

    print("=" * 70)

    print(
        "AUTOMATION ERROR"
    )

    print("=" * 70)

    print()

    print(
        "Error Type:",
        type(e).__name__
    )

    print(
        "Error:",
        str(e)
    )

    print()

    print("=" * 70)

    time.sleep(5)


finally:

    driver.quit()

    print()

    print(
        "Chrome closed."
    )
