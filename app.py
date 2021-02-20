# web app
import os
from flask import Flask, flash, redirect, url_for, render_template, request
import folium
import json
import requests

# ml
import keras
import numpy as np
from PIL import Image
import pandas as pd
from random import randint

app = Flask(__name__)
app.config['SECRET_KEY'] = "supertopsecretprivatekey"
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config["CACHE_TYPE"] = "null"
app.config.update( DEBUG=True, TEMPLATES_AUTO_RELOAD=True)


# testing stuf
@app.route('/<name>')
def home(name):
    return f"<h1>Hello {name}</h1>"

# start here
@app.route('/', methods=["POST", "GET"])
def index():
    num = -1
    img = -1
    if request.method == "POST":
        if request.files.get('img', ''):
            img = request.files.get('img', '')
            if img:
                path = os.path.join('static/img', "upload.jpg")
                img.save(path)

                img = Image.open(path).convert('L')
                img = img.resize((28, 28), Image.ANTIALIAS)
                path = os.path.join('static/img', "digit.jpg")
                img.save(path)
                data = ((np.asarray(img)) / 255.0)
                model = keras.models.load_model("digits_model.h5")
                # pred = model.predict_classes(data.reshape(1, 28, 28))
                pred = model.predict_classes(data.reshape(-1, 28 * 28))
                print(pred)
                num = pred[0]
            else:
                print(f"Nao enviou img")
                num = -2
        else:
            print(f"Nao enviou")
            num = -2

    return render_template("index.html", pred=num, disp=img)

@app.route('/housing', methods=["POST", "GET"])
def housing_prices():
    data = pd.read_csv("kc_house_data.csv")
    url = "https://raw.githubusercontent.com/python-visualization/folium/master/tests/us-counties.json"
    king = requests.get(url)
    king = king.json()

    for x in king['features']:
        if x['id'] == '53033':
            king = x
            break

    map = folium.Map(location=[47.47, -121.84],
                            tiles="OpenStreetMap",
                            zoom_start=9.5)

    folium.GeoJson(king, name="geojson").add_to(map)
    tooltip = "Click for house stats"
    for n in range(10):
        i = randint(0, 2000)
        lat = data.lat[i]
        long = data.long[i]

        bed = data.bedrooms[i]
        bath = data.bathrooms[i]
        sqft = data.sqft_lot[i]
        floors = data.floors[i]
        str = f"<i style='font-family: Helvetica, sans-serif;'>Sqft: {sqft}<br>N floors: {floors}<br>N beds: {bed}<br>N bath: {bath}</i>"

        iframe = folium.IFrame(str, width=125, height=100)
        pop = folium.Popup(iframe, max_width=125)
        folium.Marker([lat, long], popup=pop, tooltip=tooltip).add_to(map)

    map.save("templates/map.html")

    return render_template("housing.html")

@app.route('/map')
def map():
    return render_template('map.html')


if __name__ == '__main__':
    app.run(host="0.0.0.0")
