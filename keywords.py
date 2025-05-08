# keywords.py
import openai
import os
from dotenv import load_dotenv

# Ortam değişkenlerini yükle
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
openai.api_key = os.getenv('apikey')


def extract_keywords(question: str) -> list:
    """
    Soruyu alır, GPT ile anahtar kelimeleri çeker, temizlenmiş bir liste döndürür.
    """
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "sorudaki anahtar kelimeleri parça parça listele sadece kelimeleri yaz."},
            {"role": "user", "content": question}
        ],
        max_tokens=100,
        temperature=0.1
    )

    # OpenAI'den gelen yanıtı al
    keywords_response = response['choices'][0]['message']['content']

    # Temizleme işlemi
    cleaned_keywords = keywords_response.replace("Anahtar kelimeler:", "").replace("Eş anlamlılar ve benzer kelimeler:", "").strip()

    # Virgüle göre böl ve listele
    keywords_list = [keyword.strip() for keyword in cleaned_keywords.split(',') if keyword.strip()]

    return keywords_list
