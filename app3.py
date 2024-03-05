from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.document_loaders import TextLoader, DirectoryLoader
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv
import os

app = Flask(__name__)
CORS(app) 

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")


input_folder_path = "realdata"


text_loader = DirectoryLoader(input_folder_path, loader_cls=TextLoader, loader_kwargs={"encoding": "utf-8"})
documents = text_loader.load()


text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
texts = text_splitter.split_documents(documents)


persist_directory = 'db'


embedding = OpenAIEmbeddings()


vectordb = Chroma.from_documents(documents=texts,
                                 embedding=embedding,
                                 persist_directory=persist_directory)
vectordb.persist()


vectordb = Chroma(persist_directory=persist_directory, embedding_function=embedding)


retriever = vectordb.as_retriever()


turbo_llm = ChatOpenAI(temperature=0, model_name='gpt-3.5-turbo')


qa_chain = RetrievalQA.from_chain_type(llm=turbo_llm, chain_type="stuff", retriever=retriever,
                                       return_source_documents=True)


def process_llm_response(llm_response):
    response_text = llm_response['result']
    response_text = response_text.split("Sources:")[0].strip()
    return response_text


@app.route('/api/ideaentity', methods=['POST'])  
def ideaentity_api():
    user_input = request.json.get('user_input', '')
    llm_response = qa_chain(user_input)
    bot_response = process_llm_response(llm_response)
    print(bot_response) 
    return jsonify({'bot_response': bot_response})


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get-response', methods=['POST'])
def get_response():
    user_input = request.form['user_input']
    llm_response = qa_chain(user_input)
    response = process_llm_response(llm_response)
  
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
