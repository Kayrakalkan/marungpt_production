# gpt_response.py

import openai
from dotenv import load_dotenv
import os

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
openai.api_key = os.getenv('apikey')


def get_gpt_response(question: str, documents: list) -> str:
    # Elasticsearch sonuçlarını tek string haline getir
    all_contents = []
    for result in documents:
        for hit in result['hits']['hits']:
            content = hit["_source"].get("content", "")
            if content:
                all_contents.append(content)

    combined_content = "\n".join(all_contents)

    # GPT'ye gönderilecek prompt
    messages = [
        {
            "role": "system",
            "content": (
                "Soruya Marmara üniversitesinden gelen dökümanlara göre cevap vermelisin. "
                "Sana birden fazla veri gelecek ve o verilerden sana uyanı bul. "
                "Eğer uymuyorsa, 'Bununla ilgili bir bilgim yok.' de.\n\n" + combined_content
            )
        },
        {
            "role": "user",
            "content": question
        }
    ]

    # OpenAI yanıtı al
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=500,
        temperature=0.1
    )

    return response['choices'][0]['message']['content']
