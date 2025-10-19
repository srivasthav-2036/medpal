from flask import Flask,render_template,request,redirect, jsonify, send_from_directory
from markdown import markdown 
from bot.chatbot import initialize_chat_session, get_bot_reply
import pickle

app=Flask(__name__)
MODEL_PARAMS = {
    "Diabetes": [("Gender",['Male','Female']),("Age",[]),("Urea",[]), ("Cr",[]), ("HbA1c",[]), ("Cholestrol",[]),("TG",[]),("HDL",[]),("LDL",[]), ("VLDL",[]),("BMI",[])],
    "Heart Disease": [("Age",[]), ("Gender",['Male','Female']), ("Blood Pressure",[]), ("Cholesterol Level",[]), ("Exercise Habits",['High' ,'Low' ,'Medium']),("Smoking",['Yes','No']),("Family heart disease",['Yes','No']),("Diabetes",['No','Yes']),("BMI",[]),("High BP",['Yes','No']),("Low HDL Cholestrol",['Yes','No']),("High LDL Cholestrol",['Yes','No']),("Alcohol Consumption",['High' ,'Medium' ,'Low' ]),("Stress Level",['High','Medium' ,'Low']),("Sleep Hours",[]),("Sugar Consumption",['High', 'Medium','Low']),("Triglyceride Levels",[]),("Fasting Blood Sugar",[]),("CRP Levels",[]),("Homocysteine Levels",[])],
    "Liver Disease": [("Age",[]), ("Bilirubin",[]), ("AlkPhos",[]), ("Albumin",[])],
    "Kidney Disease": ["Creatinine", "BP", "Sodium", "Potassium"],
    "Lung Cancer": ["Gene_Mutation_Score", "Tumor_Size", "Age"]
}
@app.route('/')
def home():
    return render_template('index.html')

@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]
    # Verify credentials logic here
    return redirect("/predictions")

@app.route("/register")
def register():
    return render_template("register.html")


@app.route('/predictions', methods=["GET", "POST"])
def predict():
    if request.method == "POST":
        model_name = request.form.get("model_name")
        params = MODEL_PARAMS.get(model_name, [])
        return render_template("predict.html", model_name=model_name, params=params)
    return render_template("predict.html", models=MODEL_PARAMS.keys())

@app.route("/predict_result", methods=["POST"])
def predict_result():
    model_name = request.form.get("model_name")
    inputs = {k: v for k, v in request.form.items() if k != "model_name"}
    print(inputs)
    # Here you can handle model prediction logic
    model=pickle.load(open(f'models/{model_name}_model.pkl', 'rb'))
    prediction = f"Predicted {model_name} result based on inputs: {inputs}"
    return f"<h2>{prediction}</h2><a href='/predictions'>Back</a>"

# chatbot api
@app.route('/chatbot', methods=['GET', 'POST'])
def chatbot():
    reply_html = ""
    user_message = ""
    session_id = "webform"

    if request.method == 'POST':
        user_message = request.form.get('message', '').strip()
        if user_message:
            initialize_chat_session(session_id)
            reply_text = get_bot_reply(session_id, user_message)
            # Convert Markdown text → HTML for nice formatting
            reply_html = markdown(reply_text, extensions=['fenced_code', 'tables', 'nl2br'])

    return render_template('chatbot.html', user_message=user_message, reply=reply_html)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json or {}
    user_message = data.get("message", "")
    session_id = data.get("session_id", "default")

    initialize_chat_session(session_id)
    reply = get_bot_reply(session_id, user_message)

    return jsonify({"reply": reply})

# about api
@app.route('/about')
def about():
    return render_template('about.html')

if __name__=='__main__':
    app.run(debug=True)