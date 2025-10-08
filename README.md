# TitanHelp

## Project Description
The TitanHelp Ticketing System is a web-based help desk ticket management application that allows users to create, view, and close tickets. Tickets are persisted in a SQL database. The purpose of the project is to demonstrate a layered architecture approach by separating concerns between presentation, application logic, and data access layers. The project also serves as an exercise in project planning, collaboration, and GitHub version control.

## Features
- List all tickets
- Create new tickets
- View individual tickets
- Close tickets
- Persistent ticket storage using SQLite

## Technology Stack
- **Programming Language:** Python 3.x
- **Web Framework:** Flask
- **Templating Engine:** Jinja2
- **Database:** SQLite
- **Testing:** Pytest

## Installation/Setup
Clone the repository:
```bash
git clone https://github.com/stack-tracers/titanhelp.git
```

Navigate to the project folder:
```bash
cd titanhelp
```

Create a virtual environment:
```bash
python -m venv venv
```

Activate the virtual environment:
```bash
source venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application
Start the Flask server:
```bash
python app.py
```

Open the local Flask server in a web browser:
```
http://127.0.0.1:5000/
```
