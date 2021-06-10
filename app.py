from flask import Flask, render_template, request
import pickle
from processing_input import *

app = Flask(__name__)
model = pickle.load(open('model.pkl', 'rb'))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/',methods=['POST'])
def predict():
    features = [x for x in request.form.values()]
    #print (features)
    #features = ['San Francisco', '2021-06-11', '13:51', '12']
    df = process_data(features)
    #print(df)
    prediction = model.predict(df)
    output = round(prediction[0], 2)
    return render_template('index.html', prediction_text='Car rent should be ${}'.format(output))

if __name__ == "__main__" :
    app.run(debug=True) 

