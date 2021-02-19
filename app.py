# web app
import os
from flask import Flask, flash, redirect, url_for, render_template, request
import folium

# ml
import keras
import numpy as np
from PIL import Image
import pandas as pd

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
    #data = pd.read_csv("kc_house_data.csv")
    map = folium.Map(location=[47.47, -121.84],
                            zoom_start=10,
                            tiles="cartodbpositron",
                            width='75%', height = '75%')
    map.save("templates/map.html")

    return render_template("housing.html")


if __name__ == '__main__':
    app.run(debug=True)
