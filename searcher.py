import csv
import time
import numpy as np
from configuration import read
from generate_inv_list import tokenize
from manager import csv_to_dict_dict
import log


def read_queries(filename):
    queries = {}
    with open(filename, 'r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=';')
        next(reader)
        for row in reader:
            query_id, query_text = row
            queries[query_id] = tokenize(query_text)
    return queries


def get_all_docs(filename):
    docs_ids = []
    with open(filename, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=';')
        columns = reader.fieldnames
        for row in reader:
            docs_ids.append(row[columns[1]].strip())
    return set(docs_ids)


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
            sorted_docs = sorted(docs.items(), key=lambda x: x[1], reverse=True)
            for rank, (doc_id, similarity) in enumerate(sorted_docs, start=1):
                writer.writerow([query_id, rank, doc_id, similarity])


def searcher(queries, vector_model):
    similarities = create_vector_weights(queries, vector_model)
    write_rankings_to_csv(similarities, './data/output.csv')


def main():
    logger = log.setup_logger('search', 'search.log')
    start_time = time.time()
    logger.info("Inicio do Buscador")
    config = read('./instructions/BUSCA.CFG', logger)
    path = './data/'
    vector_model_path = path + config['modelo']
    queries_path = path + config['consultas']

    vector_model = csv_to_dict_dict(vector_model_path)
    queries = read_queries(queries_path)
    logger.info("Aquivos lidos {} e {}.".format(config['modelo'], config['consultas']))
    start_time_searcher = time.time()
    logger.info("Calculo de similaridade iniciado em {:.2f} segundos.".format(start_time_searcher))
    searcher(queries, vector_model)
    logger.info("Calculo de similaridade finalizado em {:.2f} segundos.".format(time.time()- start_time_searcher))
    logger.info("Buscador finalizado em {:.2f} segundos.".format(time.time() - start_time))


if __name__ == "__main__":
    main()
