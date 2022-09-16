from pprint import pprint
import nltk
nltk.download('stopwords')

from Questgen import main

def yes_no_que(text):
    qe= main.BoolQGen()
    payload = {
                "input_text": text
            }
    output = qe.predict_boolq(payload)
    return output['Boolean Questions'] # returns the boolean questions

def mcq_ques(text):
    qg = main.QGen()
    print("1")
    payload = {
            "input_text": text
        }
    output = qg.predict_mcq(payload)
    print("1")
    questions = output['questions']
    ques_ans = []
    for que in questions:
        ques_ans.append({'question':que['question_statement'],'answer': que['answer'],'options':que['options']})
    print(ques_ans)
    return ques_ans

def answer_predictor(text,que):
    answer = main.AnswerPredictor()
    payload = {
        "input_text" : text,
        "input_question" : que   
    }
    output = answer.predict_answer(payload)
    print("mcq ans")
    print(type(output))
    return output

def answer_boolean(text,que):
    payload = {
        "input_text" : text,
        "input_question" : que
    }
    answer = main.AnswerPredictor()
    output = answer.predict_answer(payload)
    print("bool ans")
    print(type(output))
    return output

# text = "Kalpana Chawla (17 March 1962  1 February 2003) was an Indian-born American astronaut and mechanical engineer who was the first woman of Indian origin to go to space."
# que = "When was kalpana chawla born"
# print(yes_no_que(text))
# print(mcq_ques(text))
# print(answer_predictor(text,que))
# print(answer_boolean(text,que))


