from flask import Flask,render_template,request
import pickle
app=Flask(__name__)
MODEL_PARAMS = {
    "Diabetes": ["Glucose", "BloodPressure", "BMI", "Age"],
    "Heart Disease": ["Age", "Cholesterol", "BP", "MaxHR"],
    "Liver Disease": ["Age", "Bilirubin", "AlkPhos", "Albumin"],
    "Kidney Disease": ["Creatinine", "BP", "Sodium", "Potassium"],
    "Cancer": ["Gene_Mutation_Score", "Tumor_Size", "Age"]
}
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predictions')
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
    # Here you can handle model prediction logic
    prediction = f"Predicted {model_name} result based on inputs: {inputs}"
    return f"<h2>{prediction}</h2><a href='/predict'>Back</a>"

if __name__=='__main__':
    app.run(debug=True)