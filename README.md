# Weather Data Ingestion/Analysis

## GIT clone
1) Clone git repo:
   > git clone "https://github.com/Metelurgy93/weather-data-ingestion-analysis.git"
2) Uncompress wx_data.zip to a path on your local machine

# ---------------------------------------------------------------------------------
## To run data ingestion/analysis on your local machine
1) Get inside the project directory
   > cd <project_directory>
2) Install Postgres:(For mac)
   > brew install postgresql
   > brew services start postgresql
3) Run the below cmd to see the version of postgres
   > postgres -V
4) Start postgres
   > psql postgres
5) Create a new user
   > postgres=# CREATE ROLE username WITH LOGIN PASSWORD 'quoted password'
6) To see the list of users and roles
   > postgres=# \du
7) To add permission to username
   > postgres=# ALTER ROLE username CREATEDB;
8) To create database
   > postgres=# CREATE DATABASE databasename;
9) To grant user 'username' permissions to access db
   > postgres=# GRANT ALL PRIVILEGES ON DATABASE databasename TO username;
10) Connect to db
   > postgres=> \connect databasename

Finally, run the below cmd to start data ingestion/analysis
Run the following cmd
   > python data_ingestion.py '/path/to/wx_data' '/path/to/logfile/log.txt'

# ---------------------------------------------------------------------------------
## To start flask webservice on your local machine
1) Get inside the project directory
   > cd <project_directory>
2) Install postgres binary in your python env
   > pip install -r requirements.txt
3) run the following cmd
   > python app.py

#### Note: python version: 3.9

The above cmd will start flask running on http://localhost:5000

To access swagger docs:
run http://localhost:5000/swagger in your browser

## Swagger API Snapshot
### open swagger_docs.pdf 