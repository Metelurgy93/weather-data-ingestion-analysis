from flask import Flask, request, render_template

from data_ingestion import connect_db

app = Flask('weather')
conn, cur = connect_db()


def query(date, date_or_year_dt, query1, query2):
    json_records = []
    if not date:
        cur.execute(query1)
        for row in cur.fetchall():
            json_dict = {}
            for i, value in enumerate(row):
                if cur.description[i][0] == date_or_year_dt:
                    json_dict[cur.description[i][0]] = str(value)
                else:
                    json_dict[cur.description[i][0]] = float(value)
            json_records.append(json_dict)
        return json_records
    else:
        cur.execute(query2)
        row = cur.fetchone()
        json_dict = {}
        for i, value in enumerate(row):
            if cur.description[i][0] == date_or_year_dt:
                json_dict[cur.description[i][0]] = str(value)
            else:
                json_dict[cur.description[i][0]] = float(value)
        return json_dict


@app.route('/api/weather', methods=["GET"])
def get_weather():
    args = request.args
    station_id = args.get("station_id", type=str)
    date = args.get("date", type=str)
    return query(date, 'date', f"SELECT * from public.{station_id}",
                 f"SELECT * from public.{station_id} where date = '{date}'")


@app.route('/api/weather/stats', methods=["GET"])
def get_weather_stats():
    args = request.args
    station_id = args.get("station_id", type=str)
    date = args.get("date", type=str)
    return query(date, 'year_dt', f"SELECT * from public.{station_id}_stats",
                 f"SELECT * from public.{station_id}_stats where year_dt = {date}")


@app.route('/api/swagger')
def get_docs():
    print('sending docs')
    return render_template('swaggerui.html')


if __name__ == "__main__":
    app.run('localhost', 5000, use_reloader=True, debug=True)
