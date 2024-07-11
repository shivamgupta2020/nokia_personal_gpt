import os
import openai
import uuid
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import pandas as pd
import pdfplumber
import json

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load your OpenAI API key
load_dotenv()
openai.api_key = os.getenv('API_KEY')

def clean_text(text):
    return ''.join(c if c.isprintable() else ' ' for c in text)

def load_data(file_path):
    if file_path.endswith('.txt'):
        with open(file_path, 'r') as file:
            return file.read()
    elif file_path.endswith('.xlsx') or file_path.endswith('.xls') or file_path.endswith('.xlsb'):
        df = pd.read_excel(file_path)
        return df.to_string(index=False)
    elif file_path.endswith('.pdf'):
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ''
        return clean_text(text)
    else:
        return ""

def query_openai(data, question):
    messages = [
        {"role": "system", "content": "You are an assistant who doesn't know anything except the data provided to you. Use the context to answer the question accurately. If the information is not in the context, say 'I don't know.'"},
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

def get_answer(data, question, personal_file_path):
    answer = query_openai(data, question)
    if "I don't know" in answer or not answer:
        personal_data = load_data(personal_file_path)
        answer = query_openai(personal_data, question)
    if "I don't know" in answer or not answer:
        return "I don't know"
    return answer

def update_personal_file(question, answer, personal_file_path):
    with open(personal_file_path, 'a') as file:
        file.write(f'Q: {question}\nA: {answer}\n\n')

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

        # Save metadata about the uploaded file
        metadata = {'filename': file.filename, 'file_path': file_path}
        with open(os.path.join(app.config['UPLOAD_FOLDER'], 'files_metadata.json'), 'a') as f:
            f.write(json.dumps(metadata) + '\n')
        return jsonify({'message': 'File uploaded successfully'})
    
@app.route('/files', methods=['GET'])
def list_files():
    files = []
    metadata_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'files_metadata.json')
    if os.path.exists(metadata_file_path):
        with open(metadata_file_path, 'r') as f:
            for line in f:
                files.append(json.loads(line))
    return jsonify(files)

@app.route('/ask', methods=['POST'])
def ask_question():
    question = request.json['question']
    filename = request.json['filename']
    
    metadata_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'files_metadata.json')
    file_path = None
    
    if os.path.exists(metadata_file_path):
        with open(metadata_file_path, 'r') as f:
            for line in f:
                file_metadata = json.loads(line)
                if file_metadata['filename'] == filename:
                    file_path = file_metadata['file_path']
                    break
    
    if not file_path or not os.path.exists(file_path):
        return jsonify({'answer': 'File not found. Please upload the file again.'}), 400
    
    data = load_data(file_path)
    personal_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'personal.txt')
    answer = get_answer(data, question, personal_file_path)
    if answer == "I don't know":
        return jsonify({'answer': answer, 'options': ['Update details', 'Leave it']})
    return jsonify({'answer': answer})

@app.route('/update_personal', methods=['POST'])
def update_personal():
    question = request.json['question']
    answer = request.json['answer']
    personal_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'personal.txt')
    update_personal_file(question, answer, personal_file_path)
    return jsonify({'message': 'personal.txt updated successfully'})

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
