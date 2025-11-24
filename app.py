from flask import Flask,render_template,request,redirect, jsonify,url_for,redirect,session,flash
from markdown import markdown 
from bot.chatbot import initialize_chat_session, get_bot_reply
import joblib,sqlite3
from datetime import datetime, timedelta
from functools import wraps
import os
from werkzeug.utils import secure_filename
from ai_modules.image_processor import ImageProcessor
from ai_modules.pdf_processor import PDFProcessor
import uuid
from lifestyle_chat import get_chat_response

app=Flask(__name__)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('vector_stores', exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user"):
            flash("You need to login first!","danger")
            return redirect(url_for("home"))  # redirect to home/login page
        return f(*args, **kwargs)
    return decorated_function


def get_greeting():
    hour = datetime.now().hour
    if hour < 12:
        return "Good Morning"
    elif hour < 18:
        return "Good Afternoon"
    else:
        return "Good Evening"
def initialize_database():
    conn = sqlite3.connect('Databases/users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  email TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL)''')
    conn.commit()
    conn.close()

app.secret_key = 'hello'
MODEL_PARAMS = {
    "Diabetes": [("Gender",['Male','Female']),("Age",[]),("Urea",[]), ("Cr",[]), ("HbA1c",[]), ("Cholestrol",[]),("TG",[]),("HDL",[]),("LDL",[]), ("VLDL",[]),("BMI",[])],
    "Heart Disease": [
    ("Age", []),
    ("Gender", ['Male', 'Female']),
    ("Blood Pressure", []),
    ("Cholesterol Level", []),
    ("Exercise Habits", ['High', 'Low', 'Medium']),
    ("Smoking", ['Yes', 'No']),
    ("Family Heart Disease", ['Yes', 'No']),
    ("Diabetes", ['No', 'Yes']),
    ("BMI", []),
    ("High Blood Pressure", ['Yes', 'No']),
    ("Low HDL Cholesterol", ['Yes', 'No']),
    ("High LDL Cholesterol", ['No', 'Yes']),
    ("Alcohol Consumption", ['High', 'Medium', 'Low']),
    ("Stress Level", ['Medium', 'High', 'Low']),
    ("Sleep Hours", []),
    ("Sugar Consumption", ['Medium', 'Low', 'High']),
    ("Triglyceride Level", []),
    ("Fasting Blood Sugar", []),
    ("CRP Level", []),
    ("Homocysteine Level", []),
    ],
    "Liver Disease": [("Age",[]), ("Bilirubin",[]), ("AlkPhos",[]), ("Albumin",[])],
    "Kidney Disease": [('Age',[]), ('bp',[]), ('sg',[]), ('al',[]), ('su',[]), ("rbc",[ 'Normal' ,'Abnormal']),("pc",['Normal','Abnormal' ]),("pcc",['Notpresent' ,'Present' ]),("ba",['Notpresent' ,'Present' ]), ('bgr',[]), ('bu',[]),
       ('sc',[]), ('sod',[]), ('pot',[]), ('hemo',[]), ('pcv',[]), ('wc',[]), ('rc',[]),("htn",['Yes', 'No' ]),("dm",['Yes' ,'No' ]),("cad",['No', 'Yes' ]),("appet",['Good' ,'Poor']),("pe",['No' ,'Yes' ]),("ane",['No' ,'Yes'])],
    "Lung Cancer": [("Gender",['Male','Female']), ("Age",[]), ("Smoking",['Yes','No']), ("Yellow Fingers",['Yes','No']), ("Anxiety",['Yes','No']), ("Peer Pressure",['Yes','No']), ("Chronic Disease",['Yes','No']), ("Fatigue",['Yes','No']), ("Allergy",['Yes','No']), ("Wheezing",['Yes','No']), ("Alcohol Consumption",['Yes','No']), ("Coughing",['Yes','No']), ("Shortness of Breath",['Yes','No']), ("Swallowing Difficulty",['Yes','No']), ("Chest Pain",['Yes','No'])]
}
@app.route('/')

def home():
    user = session.get('user')
    if user:
        username = user.split('@')[0].upper()
        greeting = get_greeting()
        return render_template('index.html', user_login=username, greeting=greeting)
    return render_template('index.html')


@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]
    conn=sqlite3.connect('Databases/users.db')
    c=conn.cursor()
    c.execute("SELECT * FROM users WHERE email=?", (email,))
    user = c.fetchone()
    conn.close()
    print("user: ",user)
    # Verify credentials logic here
    error=""
    
    if not user:
        error="Not a valid user. Please register first."
    elif user[2] != password:
        error="Invalid password. Please try again."
    if not error:
        session['user']=email
        return redirect(url_for('home'))  # Successful login
    return render_template('index.html',error=error)  # Invalid credentials

@app.route("/register",methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        if password != confirm_password:
            return render_template('register.html',error="Passwords Do not match")  # Passwords do not match
        conn=sqlite3.connect('Databases/users.db')
        c=conn.cursor()
        c.execute("SELECT * FROM users WHERE email=?", (email,))
        user = c.fetchone()
        print("users: ",user)
        if user:
            conn.close()
            return render_template('register.html',error=f"User with email {email} already exists. Please try with different email")  # User already exists
        c.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
        conn.commit()
        conn.close()
        return redirect('/')  # Registration successful
    return render_template("register.html") 

@app.route("/logout", methods=["POST"])
def logout():
    if 'user' in session:
        session.pop('user', None)
        flash("Come back soon!", "info")
        return redirect(url_for('home'))  # Redirect to home page after logout

@app.route('/predictions', methods=["GET", "POST"])
@login_required
def predict():
    if 'user' not in session:
        return redirect(url_for('home'))
    if request.method == "POST":
        model_name = request.form.get("model_name")
        params = MODEL_PARAMS.get(model_name, [])
        return render_template("predict.html", model_name=model_name, params=params)
    return render_template("predict.html", models=MODEL_PARAMS.keys())

@app.route("/predict_result", methods=["POST"])
def predict_result():
    model_name = request.form.get("model_name")
    params = MODEL_PARAMS.get(model_name, [])

    inputs = []
    i=0
    c=0
    h=0
    if model_name =="Lung Cancer":
        c=1
    elif model_name =="Heart Disease":
        c=1
        h=1
    params=MODEL_PARAMS.get(model_name, [])
    for k,v in request.form.items():
        print("key :",k)
        print("value :",v)
        
        if k != "model_name":
            if params[i][1]:  # If there are possible values, it's categorical
                if v=="Male" or v=="Female":
                    if v=="Male":
                        inputs.append(1)
                    else:
                        inputs.append(0)
                elif v=="Yes" or v=="No":
                    if v=="Yes":
                        inputs.append(c+1)
                    else:
                        inputs.append(c-h)
                elif v in ["High", "Medium", "Low"]:
                    if v=="High":
                        inputs.append(0)
                    elif v=="Medium":
                        inputs.append(2)
                    else:
                        inputs.append(1)
                elif v in ["Normal", "Abnormal"]:
                    if v=="Abnormal":
                        inputs.append(0)
                    else :
                        inputs.append(1)
                elif v in ['Notpresent' ,'Present' ]:
                    if v=="Present":
                        inputs.append(1)
                    else:
                        inputs.append(0)
                elif v in ['Good','Poor']:
                    if v=="Good":
                        inputs.append(0)
                    else:
                        inputs.append(1)

            else:  # Numerical input
                inputs.append(float(v))
            i+=1
            print(inputs)
        
    c=0
    h=0
    print(inputs)
    # Here you can handle model prediction logic
    print("model name : ",model_name)
    print(len(params),len(inputs))
    if len(inputs)!=len(params):
        return render_template("predict.html", error=" Please provide all inputs.",model_name=model_name,params=params)
    model=joblib.load(open(f'models/{model_name}.joblib', 'rb'))
    res=model.predict([inputs])
    print("model o/p : ",res)
    prediction=""
    if res[0]==1:
        prediction=f"The person is likely to have the {model_name}."
    else:
        prediction=f"The person is not likely to have the {model_name}."
   
    return render_template("predict.html", prediction=prediction,model_name=model_name,params=params)

# chatbot api
@app.route('/chatbot', methods=['GET', 'POST'])
@login_required
def chatbot():
    if 'user' not in session:
        return redirect(url_for('home'))
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

# xray api

@app.route('/xray')
@login_required
def xray():
    return render_template('xray.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Add unique identifier to avoid conflicts
        unique_filename = f"{uuid.uuid4()}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        
        # Store file info in session
        if 'uploaded_files' not in session:
            session['uploaded_files'] = []
        session['uploaded_files'].append({
            'filename': unique_filename,
            'original_name': filename,
            'filepath': filepath,
            'type': filename.rsplit('.', 1)[1].lower()
        })
        
        return jsonify({'message': 'File uploaded successfully', 'filename': unique_filename})
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/process', methods=['POST'])
def process_files():
    try:
        data = request.get_json()
        file_type = data.get('type')
        
        print(f"Processing files of type: {file_type}")
        print(f"Uploaded files in session: {session.get('uploaded_files', [])}")
        
        if file_type == 'image':
            processor = ImageProcessor()
            result = processor.process_image(session.get('uploaded_files', []))
            print(f"Image processing result: {result}")
            return jsonify({'message': 'Image processed successfully', 'result': result})
        
        elif file_type == 'pdf':
            processor = PDFProcessor()
            print("Starting PDF processing...")
            result = processor.process_pdfs(session.get('uploaded_files', []))
            print(f"PDF processing result: {result}")
            return jsonify({'message': 'PDFs processed successfully', 'result': result})
        
        return jsonify({'error': 'Invalid file type'}), 400
    
    except Exception as e:
        print(f"Error in process_files: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

@app.route('/ask', methods=['POST'])
def ask_question():
    try:
        data = request.get_json()
        question = data.get('question')
        file_type = data.get('type')
        
        print(f"Question: {question}")
        print(f"File type: {file_type}")
        
        if not question:
            return jsonify({'error': 'No question provided'}), 400
        
        if file_type == 'image':
            processor = ImageProcessor()
            response = processor.answer_question(question, session.get('uploaded_files', []))
        elif file_type == 'pdf':
            processor = PDFProcessor()
            response = processor.answer_question(question)
        else:
            return jsonify({'error': 'Invalid file type'}), 400
        
        print(f"Response: {response}")
        return jsonify({'response': response})
    
    except Exception as e:
        print(f"Error in ask_question: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/clear', methods=['POST'])
def clear_session():
    session.clear()
    return jsonify({'message': 'Session cleared'})

# lifestyle api

@app.route('/lifestyle')
@login_required
def lifestyle():
    return render_template('lifestyle.html')

@app.route("/get-response", methods=["POST"])
def get_response():
    data = request.get_json()
    user_query = data.get("query", "")
    result = get_chat_response(user_query)
    return jsonify({"response": result})

# about api
@app.route('/about')
def about():
    return render_template('about.html')

if __name__=='__main__':
    initialize_database()
    # Use environment variables for configuration
    import os
    debug_mode = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Disable file watching to prevent restarts from AI library file changes
    app.run(
        debug=debug_mode, 
        host='127.0.0.1', 
        port=5000,
        use_reloader=False  # This prevents the watchdog restarts
    )