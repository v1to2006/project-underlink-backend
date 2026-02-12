from flask import Flask, jsonify
import mysql.connector

app = Flask(__name__)

def yhteysdb ():
    return mysql.connector.connect(
         host='127.0.0.1',
         port= 3306,
         database='flight_game',
         user='root',
         password='mipa',
         autocommit=True
         )

@app.route("/")
def kotisivu():
    return "päällä"

@app.route("/iso")
def big_airports():
    yhteys = yhteysdb()
    kursori = yhteys.cursor(dictionary=True)

    haku = f"SELECT Name, iso_country FROM airport WHERE type = 'large_airport' AND continent = 'EU' "
    kursori.execute(haku)

    isotkentat = kursori.fetchall()

    return jsonify(isotkentat)




@app.route("/dbtest")
def database_testi():
    yhteys = yhteysdb()
    kursori = yhteys.cursor()

    sql_haku = """
               SELECT type, name
               FROM airport 
              WHERE iso_country = 'FI'  """


    kursori.execute(sql_haku)
    kentat = kursori.fetchall()

    kursori.close()
    yhteys.close()

    return jsonify(kentat)



if __name__ == "__main__":
    app.run(debug=True)