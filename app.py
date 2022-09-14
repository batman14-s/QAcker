import pyrebase
import speech_recognition as sr
from os import environ
import os
from flask import jsonify
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for
from dotenv import load_dotenv
import requests
from gtts import gTTS
from flask import Flask,render_template,url_for
from flask import request as req
from flask_dance.contrib.google import make_google_blueprint, google
# from question_answer.question_generator import generate_questions
# from question_generator import yes_no_que, mcq_ques, answer_boolean, answer_predictor
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
from random import randint
import nltk.data
from nltk.tokenize import sent_tokenize
import nltk
nltk.download('averaged_perceptron_tagger')
nltk.download('punkt')
nltk.download('wordnet')

## 
from crypt import methods
from operator import truediv
from transformers import pipeline
import moviepy.editor
from question_answer.question_generator import generate_questions
from summary import summarizer
import speech_recognition as sr
import os
import nltk
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer

##

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

client_id = os.getenv('GOOGLE_CLIENT_ID')
client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
app.secret_key = os.getenv('secret_key')

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

blueprint = make_google_blueprint(
    client_id=client_id,
    client_secret=client_secret,
    reprompt_consent=True,
    scope=["profile", "email"],
    offline=True,
)
app.register_blueprint(blueprint, url_prefix="/login")

#initialize firebase
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()
db.child("users")
#Initialze person as dictionary

person = {"is_logged_in": False, "name": "", "email": "", "uid": ""}
def ph(text):
    output = ""

    # Load the pretrained neural net
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

    # Tokenize the text
    tokenized = tokenizer.tokenize(text)

    # Get the list of words from the entire text
    words = word_tokenize(text)

    # Identify the parts of speech
    tagged = nltk.pos_tag(words)


    for i in range(0,len(words)):
        replacements = []

        for syn in wordnet.synsets(words[i]):

            if tagged[i][1] == 'NNP' or tagged[i][1] == 'DT':
                break

            word_type = tagged[i][1][0].lower()
            if syn.name().find("."+word_type+"."):
                # extract the word only
                r = syn.name()[0:syn.name().find(".")]
                replacements.append(r)

        if len(replacements) > 0:
            # Choose a random replacement
            replacement = replacements[randint(0,len(replacements)-1)]
            output = output + " " + replacement
        else:
            output = output + " " + words[i]

    return output

def video_to_audio(path):
    video = moviepy.editor.VideoFileClip(path)
    aud = video.audio
    aud.write_audiofile("demo.wav")
    print("--End--")

#audio_to_text
def audio_to_text(path):
    text=''
    r=sr.Recognizer()
    with sr.AudioFile(path) as source:
        audio_data = r.record(source)
        text = r.recognize_google(audio_data)
        print(text)
        return text

# Keywords Finder
def keyword_generator(text,range, top_n):
    n_gram_range = (1, range)
    stop_words = "english"
    count = CountVectorizer(ngram_range=n_gram_range, stop_words=stop_words).fit([text])
    candidates = count.get_feature_names_out()
    model = SentenceTransformer('distilbert-base-nli-mean-tokens')
    doc_embedding = model.encode([text])
    candidate_embeddings = model.encode(candidates)
    distances = cosine_similarity(doc_embedding, candidate_embeddings)
    keywords = [candidates[index] for index in distances.argsort()[0][-top_n:]]
    print(keywords)
    return keywords


#Login
@app.route("/")
def landing():
    person["is_logged_in"] = False
    person["email"] = ""
    person["uid"] = ""
    person["name"] = ""
    google_data = None
    user_info_endpoint = '/oauth2/v2/userinfo'
    if google.authorized :
        google_data = google.get(user_info_endpoint).json()
        print("okay",google_data)
        if'error' in google_data:
              return render_template("landing.html")
        print(google_data)
        person['email']=google_data['email']
        person['name']=google_data['name']
        person["is_logged_in"]=True
        data = {"name":google_data['name'], "email": google_data['email']}
        t1=db.child("users").child(google_data["id"]).set(data)
        return redirect(url_for('welcome'))
    return render_template("landing.html")
#Login
@app.route("/login")
def login():
    return render_template("login.html")

#Sign up/ Register
@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/loginwithgoogle")
def loginwithgoogle():
    return redirect(url_for('google.login'))

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
@app.route("/stt")
def stt():
    if person["is_logged_in"]==False:
        return redirect(url_for('login'))
    return render_template("stt.html")
@app.route("/paraphrase")
def paraphrase():
    if person["is_logged_in"]==False:
        return redirect(url_for('login'))
    return render_template("paraphrase.html")
@app.route("/phrase",methods=["POST"])
def phrase():
    if person["is_logged_in"]==False:
        return redirect(url_for('.'))
    sen=request.get_json()
    pem=sen['data']
    text=ph(pem)
    ata={'name':text}
    return jsonify(ata)
@app.route("/Summarize",methods=["GET","POST"])
def Summarize():
    if person["is_logged_in"]==False:
        return redirect(url_for('login'))
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
        def query3(payload):
            response = requests.post(API_URL_3, headers=headers, json=payload)
            return response.json()
        def query4(payload):
            response = requests.post(API_URL_4, headers=headers, json=payload)
            return response.json()

        output4 = query4({
            "inputs":data,
            "parameters":{"min_length":minL,"max_length":maxL},
        })[0]

        output = query({
            "inputs":data,
            "parameters":{"min_length":minL,"max_length":maxL},
        })[0]

        output2 = query2({
            "inputs":data,
            "parameters":{"min_length":minL,"max_length":maxL},
        })[0]

        # output3 = query3({
        #     "inputs":data,
        #     "parameters":{"min_length":minL,"max_length":maxL},
        # })[0]




        return render_template("index.html",result=output["summary_text"],result2=output2["summary_text"],result3=output4["summary_text"])
    else:
        return render_template("index.html")

# @app.route("/question")
# def question():
#     if person["is_logged_in"]==False:
#         return redirect(url_for('.'))
#     return render_template("ques.html")
# @app.route("/answer")
# def answer():
#     if person["is_logged_in"]==False:
#         return redirect(url_for('.'))
#     return render_template("answer.html")
# @app.route("/questions", methods = ['POST','GET'])
# def questions():
#     if person["is_logged_in"]==False:
#         return redirect(url_for('login'))
#     if request.method == 'POST':

#         # # getting data from form
#         # # getting data from form
#         print(request.form)
#         print(request.form['text_data'])
#         print(request.form['plan'])
#         text = request.form['text_data']
#         que_type = request.form['plan']
#         questions = []
#         if(que_type == "boolean"):
#             questions = yes_no_que(text) # returns list of questions

#         elif(que_type == "mcq"):
#             quest = mcq_ques(text) # returns list of dictionary --> {question, answer, options}
#             print(quest)
#             for p in quest:
#                 print(p)
#                 questions.append(p)

#         return render_template('ques.html', type = que_type, text=text, questions=questions)
#         # return redirect(url_for('.ques_gen', type = que_type, text=text, que=questions))

#     else:
#         return render_template('ques.html')

# @app.route("/answers", methods = ['POST','GET'])
# def answers():
#     if person["is_logged_in"]==False:
#         return redirect(url_for('login'))
#     if request.method == 'POST':
#         # # getting data from form
#         print(request.form)
#         print(request.form['text_data'])
#         print(request.form['plan'])
#         text = request.form['text_data']
#         que_type = request.form['plan']
#         que = request.form['question']

#         if(que_type == "boolean"):
#             answer = answer_boolean(text,que) # returns list of questions

#         elif(que_type == "mcq"):
#             answer = answer_predictor(text,que)

#         return render_template('answer.html', type = que_type, text=text, question=que, answer = answer)
#         # return redirect(url_for('.ques_gen', type = que_type, text=text, que=questions))

#     else:
#         return render_template('answer.html')

@app.route('/question_gen', methods = ['GET','POST'])
def success():
    if request.method == 'GET':
        return render_template('upload.html')
    if request.method == 'POST':
        fileType = request.form.get('type')
        if(fileType=="audio" or fileType=="video"):
            f = request.files['file']
            if(fileType=="video"):
                f.save(f.filename)
                path = f.filename
                video = moviepy.editor.VideoFileClip(path)
                video_to_audio(path)
            else:
                f.save("demo.wav")
            text = audio_to_text("demo.wav")
        # # summary_text = text_summary(text)
        else:
            text = request.form.get("inputText")
        # Generating Questions
        questions_data = generate_questions(text)
        print(questions_data)
        for item in questions_data:
            item['question']=item['question'].replace("<pad>", "")
            item['answer']=item['answer'].replace("<pad>", "")
        # Generating Keywords
        keywords=[]
        keywords.append(keyword_generator(text, 1, 5))
        keywords.append(keyword_generator(text, 2, 3))
        keywords.append(keyword_generator(text, 3, 1))
        ch1 = len(text);
        w1 = len(text.split())
        sentences = nltk.sent_tokenize(text)
        summaryLen = len(sentences)
        summary_text=summarizer(text, summaryLen//2)
        ch2 = len(summary_text);
        w2 = len(summary_text.split())
        print(summary_text)

        return render_template('summary.html', actualText = text, summary_text = summary_text, questions_data = questions_data, keywords = keywords, w1 = w1, w2 = w2, ch1 = ch1, ch2 = ch2)

@app.route("/tts", methods=["GET", "POST"])
def texttospeech():
	status = 0
	if request.method == "POST":
		if request.form.get('mp3') == "Convert":
			text_data = request.form.get('text')
			language = request.form.get('language')
			audio = gTTS(text_data, lang=language)
			audio.save("static/your_audio.mp3")
			status = 1
			return render_template("tts.html", status=status)

	return render_template("tts.html", status=status)

@app.route("/logout")
def logout():
    if google.authorized:
        token = blueprint.token["access_token"]
        resp = google.post(
            "https://accounts.google.com/o/oauth2/revoke",
            params={"token": token},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert resp.ok, resp.text
        print(google.get("/oauth2/v2/userinfo").json())
    person["is_logged_in"] = False
    person["email"] = ""
    person["uid"] = ""
    person["name"] = ""
    return render_template("landing.html")
# -----------------------------------------------------------------------------------------
# ============================================================================================


if __name__ == "__main__":
    app.run()
