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
import pickle
from sklearn.ensemble import GradientBoostingRegressor

app = Flask(__name__)
app.config['SECRET_KEY'] = "supertopsecretprivatekey"
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config["CACHE_TYPE"] = "null"
app.config.update( DEBUG=True, TEMPLATES_AUTO_RELOAD=True)

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
    conv_dates = [1 if values == 2014 else 0 for values in data.date]
    data['date'] = conv_dates

    url = "https://opendata.arcgis.com/datasets/12712f465fc44fb58328c6e0255ca27e_11.geojson?where=OBJECTID%20%3E%3D%207947%20AND%20OBJECTID%20%3C%3D%207947"
    king = requests.get(url)
    king = king.json()

    map = folium.Map(location=[47.47, -121.84],
                            tiles="OpenStreetMap",
                            zoom_start=9.4)
    style = {
        "fillOpacity": 0.1,
    }
    url = "https://skgrange.github.io/www/data/london_boroughs.json"
    london = requests.get(url)
    london = london.json()
    folium.GeoJson(king, name="King County", style_function= lambda x : style, tooltip=folium.features.GeoJsonTooltip(fields=['JURISDICT_NM',],sticky=False, labels=False, localize=True)).add_to(map)

    #folium.GeoJson(london, name="london", style_function= lambda x : style, tooltip=folium.features.GeoJsonTooltip(fields=['name',],sticky=False, labels=False, localize=True)).add_to(map)
    folium.LayerControl().add_to(map)

    tooltip = "Click for house stats"
    for n in range(15):
        i = randint(0, 2000)
        lat = data.lat[i]
        long = data.long[i]

        bed = data.bedrooms[i]
        bath = data.bathrooms[i]
        sqft = data.sqft_lot[i]
        floors = data.floors[i]
        real_price = data.price[i].round(1)

        x= data.iloc[[i]]
        x = x.drop(['id', 'price'], axis=1)
        pkl_filename = "house_model.pkl"
        with open(pkl_filename, 'rb') as file:
            model = pickle.load(file)
        pred_price = model.predict(x).round(1)

        str = f"<i style='font-family: Helvetica, sans-serif; line-height: 1.6;'>Sqft: {sqft}sq<br>N floors: {floors}<br>N beds: {bed}<br>N bath: {bath}<br>Price: {real_price}$<br>Pred. price: {pred_price[0]}$ </i>"

        iframe = folium.IFrame(str, width=200, height=120)
        pop = folium.Popup(iframe, max_width=200)
        folium.Marker([lat, long], popup=pop, tooltip=tooltip, icon=folium.Icon(color='cadetblue', icon='home', prefix='fa')).add_to(map)

    map.save("templates/map.html")

    return render_template("housing.html")

@app.route('/map')
def map():
    return render_template('map.html')


if __name__ == '__main__':
    app.run(debug=True)
