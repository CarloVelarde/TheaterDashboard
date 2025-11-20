# Theater Operations Dashboard

This is a small web app that acts as an **operations and analytics dashboard** for a single movie theater

It is _not_ a full ticketing system that involves the crud functionality a theater may need to operate. Instead, think of it as a informational panel where an admin/manager can:

- See all movies (now playing, upcoming, inactive)
- View upcoming showtimes and dynamic statuses (scheduled, in progress, completed, sold out)
- Check seat availability for a showtime
- See which concession categories bring in the most money
- View lifetime ticket sales and profit for a movie
- Look up ticket history for a customer
- Simulate a ticket purchase (which fires **stored procedures** and **triggers** in MySQL) to ensure database is working correctly and more

Tech being used:

- **MySQL 8.0** (tables, views, triggers, procedures, functions)
- **FastAPI** + `mysql-connector-python` for the backend (raw SQL)
- **Vanilla JS + HTML + CSS + Bootstrap 5** for the frontend

---

## Setup Instructions

> **Assumption:** You already have MySQL running and the database created.  
> There is a SQL setup script included in the project (`scripts` dir) that contains scripts for setting up the DB.  
> Run `define_db.sql` for the tables, triggers, functions, and procedures and run `seed_data.sql` to fill tables with demo records

### 1. Clone the project

```bash
git clone https://github.com/CarloVelarde/TheaterDashboard.git
cd TheaterDashboard
```

### 2. Backend Setup

#### Set up a virual environment

```bash
python -m venv venv
source venv/bin/activate         # Mac/Linux
# or
venv\Scripts\activate            # Windows
```

#### Install requirements/dependencies

```bash
pip install -r requirements.txt
```

#### Create a .env file at project _root_

File should consit of

```bash
DB_HOST=localhost
DB_PORT=3306
DB_USER=xxxx    # your user
DB_PASSWORD=xxxx  # your password
DB_NAME=theater_db   # default name- change if different

```

#### Run the server

```bash
uvicorn app.main:app --reload
```

#### Once server is running

- Access api docs at http://127.0.0.1:8000/docs
- Acess website at http://127.0.0.1:8000
