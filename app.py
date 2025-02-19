from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from financial_assistant import get_stock_info, get_financial_news
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.chat_models import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_document(file_path):
    try:
        if file_path.endswith('.pdf'):
            loader = PyPDFLoader(file_path)
        elif file_path.endswith('.docx'):
            loader = Docx2txtLoader(file_path)
        else:
            with open(file_path, 'r') as f:
                return f.read()
        
        # Load the document
        documents = loader.load()
        
        # Use a smaller chunk size for better processing
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        texts = text_splitter.split_documents(documents)
        
        # Use a map-reduce chain for better handling of long documents
        llm = ChatOpenAI(temperature=0.2)
        
        # Create prompt templates
        map_prompt = PromptTemplate(
            template="Write a concise summary of the following text, focusing on the main points:\n\n{text}\n\nCONCISE SUMMARY:",
            input_variables=["text"]
        )
        
        combine_prompt = PromptTemplate(
            template="Combine these summaries into a coherent summary of the entire document. Include the main themes and key points:\n\n{text}\n\nCOMPREHENSIVE SUMMARY:",
            input_variables=["text"]
        )
        
        # Create the chain with the prompts
        chain = load_summarize_chain(
            llm,
            chain_type="map_reduce",
            map_prompt=map_prompt,
            combine_prompt=combine_prompt,
            verbose=True
        )
        
        summary = chain.run(texts)
        
        # Add document statistics
        num_pages = len(documents)
        total_words = sum(len(doc.page_content.split()) for doc in documents)
        
        return f"""Document Analysis Summary:
Number of Pages: {num_pages}
Total Words: {total_words}

Executive Summary:
{summary}"""
        
    except Exception as e:
        return f"Error processing document: {str(e)}"

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        try:
            summary = process_document(filepath)
            return jsonify({'summary': summary})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    return jsonify({'error': 'File type not allowed'}), 400

@app.route('/api/stock/<ticker>', methods=['GET'])
def stock_info(ticker):
    try:
        info = get_stock_info(ticker)
        return jsonify({'info': info})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/news/<query>', methods=['GET'])
def financial_news(query):
    try:
        news = get_financial_news(query)
        return jsonify({'news': news})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
