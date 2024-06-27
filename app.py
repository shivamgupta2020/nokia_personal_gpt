import os
import openai
import uuid
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import pandas as pd

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load your OpenAI API key
load_dotenv()
openai.api_key = os.getenv('API_KEY')

def load_data(file_path):
    if file_path.endswith('.txt'):
        with open(file_path, 'r') as file:
            return file.read()
    elif file_path.endswith('.xlsx') or file_path.endswith('.xls') or file_path.endswith('.xlsb'):
        df = pd.read_excel(file_path)
        return df.to_string(index=False)
    else:
        return ""

def query_openai(data, question):
    messages = [
        {"role": "system", "content": "You are an assistant. Use the context to answer the question accurately. If the information is not in the context, say 'I don't know.'"},
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
        file_ext = file.filename.split('.')[-1]
        unique_filename = f'{uuid.uuid4()}.{file_ext}'
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        # Save the path of the most recently uploaded file
        with open(os.path.join(app.config['UPLOAD_FOLDER'], 'latest_file.txt'), 'w') as f:
            f.write(file_path)
        return jsonify({'message': 'File uploaded successfully'})

@app.route('/ask', methods=['POST'])
def ask_question():
    question = request.json['question']
    latest_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'latest_file.txt')
    
    if not os.path.exists(latest_file_path):
        return jsonify({'answer': 'Please upload a file first.'}), 400
    
    with open(latest_file_path, 'r') as f:
        file_path = f.read().strip()
    
    if not os.path.exists(file_path):
        return jsonify({'answer': 'File not found. Please upload a file again.'}), 400
    
    data = load_data(file_path)
    answer = get_answer(data, question)
    return jsonify({'answer': answer})

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
