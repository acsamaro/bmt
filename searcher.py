import csv
from collections import defaultdict
import numpy as np
from itertools import combinations
from generate_inv_list import tokenize


def csv_to_dict_dict(filename):
    d = defaultdict(dict)
    with open(filename, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=';')
        columns = reader.fieldnames
        for row in reader:
            key1 = row[columns[0]].strip()
            key2 = row[columns[1]].strip()
            value = float(row[columns[2]].strip())
            d[key1][key2] = value
    return d

def get_all_docs(filename):
    docs_ids = []
    with open(filename, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=';')
        columns = reader.fieldnames
        for row in reader:
            docs_ids.append(row[columns[1]].strip())
    return set(docs_ids)

def read_queries(filename):
    queries = {}
    with open(filename, 'r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=';')
        next(reader)
        for row in reader:
            query_id, query_text = row
            queries[query_id] = tokenize(query_text)
    return queries


def cosine_similarity(vector_a, vector_b):
    keys = set(vector_a.keys()).union(set(vector_b.keys()))
    vector_a_np = np.array([vector_a.get(key, 0) for key in keys])
    vector_b_np = np.array([vector_b.get(key, 0) for key in keys])
    
    dot_product = np.dot(vector_a_np, vector_b_np)
    norm_a = np.linalg.norm(vector_a_np)
    norm_b = np.linalg.norm(vector_b_np)
    
    if norm_a == 0 or norm_b == 0:
        return 0
    return dot_product / (norm_a * norm_b)


def compare_all_documents(doc_vectors):
    results = defaultdict(dict)

    for doc_id1, doc_id2 in combinations(doc_vectors.keys(), 2):
        sim = cosine_similarity(doc_vectors[doc_id1], doc_vectors[doc_id2])
        results[doc_id1][doc_id2] = sim
    return results


def process_queries_and_calculate_similarities(queries, doc_vectors):
    results = {}
    for query_id, query_text in queries.items():
        similarities = []
        for doc_id, doc_vector in doc_vectors.items():
            sim = cosine_similarity(query_text, doc_vector)
            similarities.append((sim, doc_id))
        # Ordena os documentos pela similaridade (decrescente)
        similarities.sort(reverse=True, key=lambda x: x[0])
        # Formata a saída como uma lista de rankings
        formatted_results = [(idx + 1, sim[1], sim[0]) for idx, sim in enumerate(similarities)]
        results[query_id] = formatted_results
    return results

def save_results_to_csv(results, output_filename):
    """ Salva os resultados formatados em um arquivo CSV. """
    with open(output_filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow(['QueryNumber', 'Ranking', 'Doc', 'Similaridade'])
        for query_id, ranks in results.items():
            for rank in ranks:
                writer.writerow([query_id] + list(rank))


def create_vector_weights(query, vetorial_model):
    similarities = {}
    for query_id, tokens in query.items():
        query_vector = {token: 1 for token in tokens}
        doc_vector = {}
        for token in tokens:
            if vetorial_model.get(token) is not None:
                for doc_id, weight in vetorial_model[token].items():
                    if doc_id not in doc_vector:
                        doc_vector[doc_id] = {}
                    doc_vector[doc_id][token]= float(weight)
        similarities[query_id] = {}
        for doc_id, doc_vec in doc_vector.items():
            similarity = cosine_similarity(query_vector, doc_vec)
            similarities[query_id][doc_id] = similarity

    return similarities


def write_rankings_to_csv(similarities, output_filename):
    with open(output_filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow(['QueryNumber', 'Ranking', 'Doc', 'Similarity'])
        
        for query_id, docs in similarities.items():
            sorted_docs = sorted(docs.items(), key=lambda x: x[1], reverse=True)  # Ordena os documentos por similaridade, descendente
            for rank, (doc_id, similarity) in enumerate(sorted_docs, start=1):
                writer.writerow([query_id, rank, doc_id, similarity])

filename = './data/tfidf.csv'
doc_vectors = csv_to_dict_dict(filename)
queries = read_queries('./data/consultas.csv')
# similarities = compare_all_documents(doc_vectors)
similarities = create_vector_weights(queries, doc_vectors)
write_rankings_to_csv(similarities, './data/output.csv')