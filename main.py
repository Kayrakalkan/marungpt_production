from flask import Flask, request, jsonify
from gpt_answer import get_gpt_response
from es_search import search_documents
from keywords import extract_keywords
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
import os
from bson.objectid import ObjectId

# Ortam değişkenlerini yükle
load_dotenv()

# Flask uygulamasını başlat
app = Flask(__name__)

# MongoDB bağlantısı
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client.ai_test
collection = db.questions_answers

@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.get_json()
    question = data.get('question')

    if not question:
        return jsonify({"error": "Soru gönderilmedi"}), 400

    try:
        # 1. Anahtar kelimeleri çıkar
        keywords_list = extract_keywords(question)

        # 2. Elasticsearch'te ilgili belgeleri bul
        documents = search_documents(keywords_list)

        # 3. GPT'den yanıt al
        answer = get_gpt_response(question, documents)

        # 4. MongoDB'ye kaydet
        document = {
            "question": question,
            "answer": answer,
            "timestamp": datetime.utcnow()
        }
        result = collection.insert_one(document)

        # 5. Yanıtı döndür
        return jsonify({
            "id": str(result.inserted_id),
            "question": question,
            "answer": answer
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def hello_world():
    return "Hello MarunGpt!"

@app.route('/get_answer/<string:id>', methods=['GET'])
def get_answer(id):
    try:
        # MongoDB'den ID'ye göre veriyi al
        document = collection.find_one({"_id": ObjectId(id)})
        if not document:
            return jsonify({"error": "Soru bulunamadı"}), 404

        return jsonify({
            "id": str(document["_id"]),
            "question": document["question"],
            "answer": document["answer"],
            "timestamp": document["timestamp"]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True)
