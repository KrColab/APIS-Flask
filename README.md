# APIS-Flask

> A practical Flask REST API for querying student data, updating records, and predicting future test scores.

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-REST%20API-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Deployment](https://img.shields.io/badge/Deployment-Gunicorn-499848?logo=gunicorn&logoColor=white)](https://gunicorn.org/)

## Overview

APIS-Flask is a lightweight REST API built with Python and Flask. It provides a clean interface for searching and updating student records, experimenting with filtering, and generating score predictions from historical test results.

The project demonstrates practical backend engineering concepts, including:
- RESTful API design
- Query parameter filtering
- JSON data persistence
- Input validation
- Linear regression with NumPy
- Browser-based API interaction
- Gunicorn deployment

## Features

| Feature | Description |
| --- | --- |
| Student search | Retrieve all students or filter by city, gender, name, ID, or birth year |
| Student updates | Modify matching student records with a `PATCH` request |
| Score prediction | Predict a sixth test score using five previous scores |
| Browser UI | Explore student data through an interactive web interface |
| CORS support | Enable frontend clients to communicate with the API |
| Production entry point | Run the application with Gunicorn |

## Technology Stack

- Python
- Flask
- Flask-CORS
- NumPy
- JSON
- Gunicorn

## Getting Started

### Clone the repository

```bash
git clone https://github.com/KrColab/APIS-Flask.git
cd APIS-Flask
```

### Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

For Windows PowerShell:

```powershell
.venv\Scripts\activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run the application

```bash
python app.py
```

The API will be available at:

```text
http://127.0.0.1:5001
```

Open the interactive browser interface at:

```text
http://127.0.0.1:5001/ui
```

## API Documentation

### Get students

```http
GET /Students
```

Retrieve all student records:

```bash
curl http://127.0.0.1:5001/Students
```

Supported filters:
- `City` or `Town`
- `Gender`
- `Name`
- `id` or `Id`
- `minYear`
- `maxYear`

Examples:

```bash
curl "http://127.0.0.1:5001/Students?City=Kosice"
```

```bash
curl "http://127.0.0.1:5001/Students?Gender=Female"
```

```bash
curl "http://127.0.0.1:5001/Students?minYear=1995&maxYear=2005"
```

```bash
curl "http://127.0.0.1:5001/Students?Name=anna"
```

The endpoint returns a JSON array containing matching student records.

### Update students

```http
PATCH /Students
```

Update records matching the selected filters:

```bash
curl -X PATCH \
  "http://127.0.0.1:5001/Students?id=1" \
  -H "Content-Type: application/json" \
  -d '{"Gender":"Female"}'
```

Example response:

```json
{
  "updated": 1
}
```

Changes are persisted to `students.json`.

> **Note:** For a production environment, the JSON storage layer should be replaced with a database and write operations should be protected with authentication and authorization.

### Predict a future score

```http
GET /Predict?Scores=10 20 30 40 50
```

The prediction endpoint uses linear regression to estimate the score for a sixth test based on five previous scores.

```bash
curl "http://127.0.0.1:5001/Predict?Scores=10%2020%2030%2040%2050"
```

Example response:

```json
{
  "prediction": 60.0
}
```

The result is limited to the range `0..100` and rounded to two decimal places. The API validates that exactly five numeric scores are provided.

### Web interface

- `GET /ui` opens the interactive student filtering interface.
- `GET /` redirects to the web interface.

## Production Deployment

The repository includes a `Procfile` configured for Gunicorn:

```bash
gunicorn app:app
```

This command can be used by hosting platforms such as Render, Railway, Heroku-style services, or other Python-compatible deployment environments.

## Project Structure

```text
.
├── app.py
├── students.json
├── templates/
│   └── filter.html
├── requirements.txt
└── Procfile
```

## Engineering Highlights

This project focuses on building a simple but complete backend service with readable routes, predictable JSON responses, input validation, and deployment support.

Potential future improvements include:
- Database-backed persistence
- Automated unit and integration tests
- API documentation with OpenAPI/Swagger
- Authentication and authorization
- Structured logging
- Rate limiting
- Docker support
- CI/CD integration

## License

No license has been specified yet. Add a license before distributing or reusing this project publicly.
