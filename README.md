# String Analyzer API

A RESTful API service that analyzes strings and stores their computed properties.

## Features

- Analyze string properties (length, palindrome, word count, etc.)
- SHA-256 hashing for unique identification
- Advanced filtering capabilities
- Natural language query support
- RESTful endpoints with proper HTTP status codes

## Local Development

### Prerequisites
- Python 3.8+
- pip

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd string-analyzer-api
Create virtual environment:

bash
python -m venv venv
source venv/bin/activate  or  venv\Scripts\activate On Windows
Install dependencies:

bash
pip install -r requirements.txt
Set up environment variables:

bash
cp .env.example .env
Run migrations:

bash
python manage.py migrate
Start development server:

bash
python manage.py runserver
The API will be available at http://localhost:8000/api/

API Endpoints
POST /api/strings
Analyze a new string.

GET /api/strings/{string_value}
Get analysis for a specific string.

GET /api/strings
Get all analyses with filtering.

GET /api/strings/filter-by-natural-language
Natural language query interface.

DELETE /api/strings/{string_value}
Delete a string analysis.

Dependencies
Django 4.2+

Django REST Framework 3.14+

django-filter 23.0+

Deployment
This application can be deployed on:

Railway

Heroku

AWS Elastic Beanstalk

PythonAnywhere

DigitalOcean App Platform