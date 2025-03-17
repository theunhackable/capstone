## SETUP

- create a `venv` using `python -m venv venv`.
- activate `venv` using command specific to your operating system.
- use `pip install -r requirements.txt` to install all the dependencies.
- rename `.example.env` file to `.env` file and uncomment/change the variables.
- use `docker compose up` to spin the mysql container.
- use`flask db init`, `flask db migrate` and `flask db upgrade` for making the db reflect changes
- use `python run.py` to run the app
