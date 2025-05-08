# es_search.py
from elasticsearch import Elasticsearch
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

ELASTICSEARCH_URL = os.getenv('ELASTICSEARCH_URL')
ELASTICSEARCH_API_KEY = os.getenv('ELASTICSEARCH_API_KEY')

client = Elasticsearch(
    ELASTICSEARCH_URL,
    api_key=ELASTICSEARCH_API_KEY
)

indices = [
     "spor", "yurtlar"
]


def search_in_index(index_name, keywords_list, fields=["content"]):
    search_body = {
        "query": {
            "bool": {
                "should": [
                    {
                        "multi_match": {
                            "query": keyword,
                            "fields": fields,
                            "type": "best_fields",
                            "operator": "and",
                            "fuzziness": "AUTO"
                        }
                    }
                    for keyword in keywords_list
                ]
            }
        }
    }
    response = client.search(index=index_name, body=search_body)
    return response


def search_documents(keywords_list):
    final_results = []

    # 1. Adım: Index adı ve keyword eşleşmesi
    matching_indices = [index for index in indices if any(keyword.lower() in index.lower() for keyword in keywords_list)]

    if matching_indices:
        for index in matching_indices:
            title_search_result = search_in_index(index, keywords_list, fields=["title"])
            if title_search_result['hits']['total']['value'] > 0:
                final_results.append(title_search_result)
            else:
                content_search_result = search_in_index(index, keywords_list)
                final_results.append(content_search_result)
    else:
        # 2. Adım: Tüm indexlerde title araması
        title_search_results = []
        for index in indices:
            title_search_result = search_in_index(index, keywords_list, fields=["title"])
            if title_search_result['hits']['total']['value'] > 0:
                title_search_results.append(title_search_result)

        if title_search_results:
            final_results.extend(title_search_results)
        else:
            # 3. Adım: Tüm indexlerde içerik araması
            for index in indices:
                content_search_result = search_in_index(index, keywords_list)
                final_results.append(content_search_result)

    return final_results
