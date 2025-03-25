# Afyalink Web Application

A web-based application for visualizing and managing health facilities using an interactive map interface.

## Features

- Interactive map interface using Leaflet.js
- Display of health facilities with detailed information
- Filtering facilities by type
- Responsive design for all devices
- PostgreSQL integration with GIS support

## Prerequisites

- Python 3.8+
- PostgreSQL with PostGIS extension
- pip (Python package manager)

## Installation

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Linux/Mac
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

3. Configure the database:
- Database name: afyalink_db
- Username: kevin
- Password: admin

4. Run the application:
```bash
python app.py
```

5. Access the application at: http://localhost:5000

## Project Structure

```
web_app/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── static/            # Static files (CSS, JS)
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── map.js
├── templates/         # HTML templates
│   └── index.html
└── README.md         # Project documentation
```
