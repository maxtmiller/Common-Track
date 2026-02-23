
# `CommonTrack`

![Python](https://img.shields.io/badge/Python-3776AB?style=flat\&logo=python\&logoColor=white) ![Flask](https://img.shields.io/badge/Flask-000000?style=flat\&logo=flask\&logoColor=white) ![SQL](https://img.shields.io/badge/SQL-4479A1?style=flat\&logo=postgresql\&logoColor=white)

**Simplifying college applications with organized tracking, rankings, and deadlines for the Common App.**

---

## Preview

<img width="1708" height="971" alt="Screenshot 2026-02-23 at 2 28 13 AM" src="https://github.com/user-attachments/assets/d370a78f-aa46-413b-bf27-e2823bd6ded0" />

---

## Features

* Home Page with purpose, ranking criteria, and explanations
* My College List to track up to 20 colleges and sync deadlines to Google Calendar
* Search All Colleges across the full Common App database
* Ranked Colleges with QS scores and detailed criteria
* About Section detailing motivation and inspiration behind the app

---

## Technical Overview

* **Backend:** Python, Flask
* **Database:** CS50 SQL for managing college and user data
* **Security:** Werkzeug for password hashing and secure login
* **Session Management:** Functools for login redirection
* **APIs:** Google Calendar API for syncing deadlines

---

## Setup

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd CommonTrack
   ```
2. Create and activate a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```
4. Run the Flask app:

   ```bash
   flask run
   ```
5. Open the local host link in your browser.
