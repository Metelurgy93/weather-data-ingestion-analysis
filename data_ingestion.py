import sys
from datetime import datetime

import psycopg2
import os
from dotenv import dotenv_values

db_params = dict(dotenv_values(".env"))


def loging(text, log_file):
    """
    This method Logs messages to a file
    :param text: message to be logged
    :param log_file: file path where the message will be logged
    :return:
    """
    with open(log_file, 'a') as log:
        log.write(f'{datetime.now()} - {text}\n')


def connect_db():
    """
    Set up database connection
    :return: connection, cursor
    """
    connection = psycopg2.connect(**db_params)
    cursor = connection.cursor()
    return connection, cursor


def ingest_weather_data(directory: str, log_file: str):
    """
    This method ingest data into tables and creates a new table for aggregation of
    data per year for all weather stations
    :param directory:
    :param log_file:
    :return:
    """
    # get db connection and cursor object
    conn, cur = connect_db()
    try:
        # Loop through all files in the directory
        for file_name in os.listdir(directory):
            table_name = file_name.split('.')[0]
            if file_name.endswith(".txt"):
                # create a DB
                cur.execute(f"""CREATE TABLE IF NOT EXISTS public.{table_name}(
                            date date,
                            maxtemp numeric,
                            mintemp numeric,
                            precipitation numeric)""")

                with open(os.path.join(directory, file_name), 'r') as file:
                    # Read the contents of the text file
                    contents = file.readlines()
                    # Check if record already exists in database
                    cur.execute(f"SELECT * FROM public.{table_name} WHERE date = %s",
                                (contents[0].split('\t')[0],))
                    # gets one record
                    existing_record = cur.fetchone()
                    if existing_record:
                        loging(f"Table {table_name} Skipped duplicate record\n", log_file)
                    else:
                        dates = []
                        for i, row in enumerate(contents):
                            row_split = [item.strip() for item in row.split('\t')]
                            # Insert the contents into the table
                            cur.execute(
                                f"INSERT INTO public.{table_name} "
                                f"(date, maxtemp, mintemp, precipitation) "
                                f"VALUES (%s, %s, %s, %s)",
                                (datetime.strptime(row_split[0], '%Y%m%d'), float(row_split[1]),
                                 float(row_split[2]), float(row_split[3])))
                            conn.commit()
                            if i == 0 or i == len(contents) - 1:
                                dates.append(row_split[0])
                            loging(f"Records inserted in table {table_name} with start date:"
                                   f" {dates[0]} and end date: {dates[1]}\n", log_file)

                    # Creates analysis tables for each weather stations
                    cur.execute(f"""CREATE TABLE IF NOT EXISTS public.{table_name}_stats(
                            year_dt numeric,
                            avg_maxtemp numeric,
                            avg_mintemp numeric,
                            total_precipitation numeric)""")

                    # Check if record already exists in the table
                    cur.execute(f"SELECT * FROM public.{table_name}_stats WHERE year_dt = %s",
                                (contents[0].split('\t')[0][:4],))
                    existing_stats_record = cur.fetchone()
                    if existing_stats_record:
                        loging(f"Table {table_name}_stats Skipped duplicate record\n", log_file)
                    else:
                        # calculate avg_max_temp, avg_min_temp, total_accumulated_precipitation
                        # every year for every weather station
                        cur.execute(f"""INSERT INTO public.{table_name}_stats 
                            SELECT extract(year from date) as year_dt,
                                   avg(maxtemp) as avg_maxtemp,
                                   avg(mintemp) as avg_mintemp,
                                   sum(precipitation) as total_precipitation
                            FROM public.{table_name}
                            GROUP by year_dt""")
                        # commits the sql statement
                        conn.commit()
                        loging(f"Records inserted in table {table_name}_stats", log_file)
            else:
                continue
    finally:
        # Close database connection
        cur.close()
        conn.close()


if __name__ == "__main__":
    # Set up directory where the text files are stored
    directory = sys.argv[1]
    # Set up logging path
    log_file = sys.argv[2]
    # call ingest method to start creating tables
    ingest_weather_data(directory, log_file)
