import os
import openai
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load your OpenAI API key
openai.api_key = os.getenv('API_KEY')

def load_data(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def query_openai(data, question):
    messages = [
        {"role": "system", "content": f"You are an assistant. Use the context to answer the question accurately. If the information is not in the context, say 'I don't know.'"},
        {"role": "system", "content": f"Context:\n{data}"},
        {"role": "user", "content": f"Q: {question}\nA:"}
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=150,
        n=1,
        stop=["\n"]
    )
    answer = response.choices[0].message['content'].strip()
    return answer

def get_answer(data, question):
    answer = query_openai(data, question)
    if "I don't know" in answer or not answer:
        return "I don't know"
    return answer

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file1' not in request.files:
        return jsonify({'message': 'No file part'}), 400
    file = request.files['file1']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
    if file:
        filename = 'file1.txt'
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({'message': 'File uploaded successfully'})

@app.route('/ask', methods=['POST'])
def ask_question():
    question = request.json['question']
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'file1.txt')
    
    if not os.path.exists(file_path):
        return jsonify({'answer': 'Please upload a file first.'}), 400
    
    data = load_data(file_path)
    answer = get_answer(data, question)
    return jsonify({'answer': answer})

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
