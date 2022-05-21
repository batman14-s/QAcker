import pyrebase
import speech_recognition as sr
from os import environ
import os
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for
from dotenv import load_dotenv
import requests
from flask import Flask,render_template,url_for
from flask import request as req

load_dotenv()
app = Flask(__name__)
     #Initialze flask constructor
#Add your own details
config = {
  "apiKey":environ.get("API_KEY") ,
  "authDomain":environ.get("AUTH_DOMAIN"),
  "storageBucket":environ.get("STORAGE_BUCKET"),
  "databaseURL":environ.get("DATABASE_URL")
}

#initialize firebase
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()
db.child("users")
#Initialze person as dictionary

person = {"is_logged_in": False, "name": "", "email": "", "uid": ""}
db.child("users").child(person["uid"]).push({})
#Login
@app.route("/")
def login():
    return render_template("login.html")

@app.route("/logout")
def logout():
    person["is_logged_in"] = False
    person["email"] = ""
    person["uid"] = ""
    person["name"] = ""
    return redirect(url_for('login'))
#Sign up/ Register
@app.route("/signup")
def signup():
    return render_template("signup.html")

#Welcome page
@app.route("/welcome",methods=["POST","GET"])
def welcome():
    if person["is_logged_in"] == True:
        transcript = ""
        if request.method == "POST":
            print("FORM DATA RECEIVED")

            if "file" not in request.files:
                return redirect(request.url)

            file = request.files["file"]
            if file.filename == "":
                return redirect(request.url)

            if file:
                recognizer = sr.Recognizer()
                audioFile = sr.AudioFile(file)
                with audioFile as source:
                    data = recognizer.record(source)
                transcript = recognizer.recognize_google(data, key=None)
            return render_template("welcome.html", email = person["email"], name = person["name"],transcript=transcript)
        else:
            return render_template("welcome.html", email = person["email"], name = person["name"],transcript="")
    else:
        return redirect(url_for('login'))

#If someone clicks on login, they are redirected to /result
@app.route("/result", methods = ["POST", "GET"])
def result():
    if request.method == "POST":        #Only if data has been posted
        result = request.form           #Get the data
        email = result["email"]
        password = result["pass"]
        try:
            #Try signing in the user with the given information
            user = auth.sign_in_with_email_and_password(email, password)
            #Insert the user data in the global person
            global person
            person["is_logged_in"] = True
            person["email"] = user["email"]
            person["uid"] = user["localId"]
            #Get the name of the user
            data = db.child("users").child(person["uid"]).get()
            print(data.val())
            person["name"] = data.val()["name"]
            # print("heloo",person["name"])
            # #Redirect to welcome page
            return redirect(url_for('welcome'))
        except:
            #If there is any error, redirect back to login
            return redirect(url_for('login'))
    else:
        if person["is_logged_in"] == True:
            return redirect(url_for('welcome'))
        else:
            return redirect(url_for('login'))

#If someone clicks on register, they are redirected to /register
@app.route("/register", methods = ["POST", "GET"])
def register():
    if request.method == "POST":        #Only listen to POST
        result = request.form           #Get the data submitted
        email = result["email"]
        password = result["pass"]
        name = result["name"]
        try:
            #Try creating the user account using the provided data
            auth.create_user_with_email_and_password(email, password)
            #Login the user
            user = auth.sign_in_with_email_and_password(email, password)
            #Add data to global person
            global person
            person["is_logged_in"] = True
            person["email"] = user["email"]
            person["uid"] = user["localId"]
            person["name"] = name
            #Append data to the firebase realtime database
            data = {"name": name, "email": email}
            t1=db.child("users").child(person["uid"]).set(data)
            #Go to welcome page
            return redirect(url_for('welcome'))
        except:
            #If there is any error, redirect to register
            return redirect(url_for('signup'))

    else:
        if person["is_logged_in"] == True:
            return redirect(url_for('welcome'))
        else:
            return redirect(url_for('register'))
# -----------------------------------------------------------------------------------------
# ====================================TEXT SUMMARIZER========================================================
# app = Flask(__name__)
@app.route("/home",methods=["GET","POST"])
def Home():
    if person["is_logged_in"]==False:
        return render_template("signup.html")
    return render_template("index.html")

@app.route("/Summarize",methods=["GET","POST"])
def Summarize():
    if req.method== "POST":
        API_URL = "https://api-inference.huggingface.co/models/sshleifer/distilbart-cnn-6-6"
        API_URL_2 = "https://api-inference.huggingface.co/models/google/pegasus-xsum"
        API_URL_3 = "https://api-inference.huggingface.co/models/philschmid/distilbart-cnn-12-6-samsum"
        API_URL_4 = "https://api-inference.huggingface.co/models/knkarthick/MEETING_SUMMARY"

        headers = {"Authorization": "Bearer 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"}


        data=req.form["data"]

        maxL=int(req.form["maxL"])
        # maxL=70
        minL=maxL//4
        # minL=20

        def query(payload):
            response = requests.post(API_URL, headers=headers, json=payload)
            return response.json()
        def query2(payload):
            response = requests.post(API_URL_2, headers=headers, json=payload)
            return response.json()
        # def query3(payload):
        #     response = requests.post(API_URL_3, headers=headers, json=payload)
        #     return response.json()
        # def query4(payload):
        #     response = requests.post(API_URL_4, headers=headers, json=payload)
        #     return response.json()

        output = query({
            "inputs":data,
            "parameters":{"min_length":minL,"max_length":maxL},
        })[0]
        # output2 = query2({
        #     "inputs":data,
        #     "parameters":{"min_length":minL,"max_length":maxL},
        # })
        # output3 = query3({
        #     "inputs":data,
        #     "parameters":{"min_length":minL,"max_length":maxL},
        # })[0]
        # output4 = query4({
        #     "inputs":data,
        #     "parameters":{"min_length":minL,"max_length":maxL},
        # })[0]

        return render_template("index.html",result=output["summary_text"])
    else:
        return render_template("index.html")


# -----------------------------------------------------------------------------------------
# ============================================================================================


if __name__ == "__main__":
    app.run()
