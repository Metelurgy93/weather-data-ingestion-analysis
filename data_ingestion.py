from datetime import datetime

import psycopg2
import os


def loging(text):
    with open(log_file, 'a') as log:
        log.write(f'{datetime.now()} - {text}\n')


def connect_db():
    # Set up database connection
    connection = psycopg2.connect(database="weatherdb", user="tabs", password="tabs",
                                  host="localhost", port="5432")
    cursor = connection.cursor()
    return connection, cursor


conn, cur = connect_db()
# Set up directory where the text files are stored
directory = '/Users/devishmundra/Desktop/code-challenge-template-main/wx_data'

# Set up logging
log_file = '/Users/devishmundra/Documents/Code/codingTest/log/weatherlog.txt'

# Loop through all files in the directory
num_ingested = 0
# Loop through all files in the directory
for filename in os.listdir(directory):
    tablename = filename.split('.')[0]
    if filename.endswith(".txt"):
        # create a DB
        cur.execute(f"""CREATE TABLE IF NOT EXISTS public.{tablename}(
                    date date,
                    maxtemp numeric,
                    mintemp numeric,
                    precipitation numeric)""")

        cur.execute(f"""CREATE TABLE IF NOT EXISTS public.{tablename}_stats(
                    year_dt numeric,
                    avg_maxtemp numeric,
                    avg_mintemp numeric,
                    total_precipitation numeric)""")

        with open(os.path.join(directory, filename), 'r') as file:
            # Read the contents of the text file
            contents = file.readlines()
            # Check if record already exists in database
            cur.execute(f"SELECT * FROM public.{tablename} WHERE date = %s",
                        (contents[0].split('\t')[0],))
            existing_record = cur.fetchone()
            if existing_record:
                loging(f"Table {tablename} Skipped duplicate record\n")
            else:
                dates = []
                for i, row in enumerate(contents):
                    row_split = [item.strip() for item in row.split('\t')]
                    # Insert the contents into the database
                    cur.execute(
                        f"INSERT INTO public.{tablename} (date, maxtemp, mintemp, precipitation) VALUES (%s, %s, %s, %s)",
                        (datetime.strptime(row_split[0], '%Y%m%d'), float(row_split[1]),
                         float(row_split[2]), float(row_split[3])))
                    conn.commit()
                    if i == 0 or i == len(contents) - 1:
                        dates.append(row_split[0])
                    loging(f"Records inserted in table {tablename} with start date:"
                           f" {dates[0]} and end date: {dates[1]}\n")
                # calculate avg_max_temp, avg_min_temp, total_accumulated_precipitation
                # every year for every weather station
                cur.execute(f"""INSERT INTO public.{tablename}_stats 
                    SELECT extract(year from date) as year_dt,
                           avg(maxtemp) as avg_maxtemp,
                           avg(mintemp) as avg_mintemp,
                           sum(precipitation) as total_precipitation
                    FROM public.{tablename}
                    GROUP by year_dt;""")
                conn.commit()
                loging(f"Records inserted in table {tablename}_stats")
    else:
        continue

# Close database connection
cur.close()
conn.close()
