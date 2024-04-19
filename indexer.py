import csv
from collections import defaultdict, Counter
import math

def add_dict(d:dict, key:str, value:int):
    if (key not in d):
        d[key] = []
    d[key] = value

def read_inv_list_csv(filename):
    data_dict = {}
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        for row in reader:
            key = row[0]
            values = row[1].strip('[]').split(',')
            values = list(map(int, values))
            data_dict[key] = values
    return data_dict

data = read_inv_list_csv('./data/inv_list.csv')
print(data)

def compute_tf(data:dict):
    tf_scores = {}
    for word, frequencies in data.items():
        doc_tf = {}
        for doc_id, freq in enumerate(frequencies, start=1):
            max_freq = max(frequencies) if frequencies else 1
            tf = freq / max_freq
            add_dict(doc_tf, doc_id, tf)
        tf_scores[word] = doc_tf
    return tf_scores


tf_scores = compute_tf(data)
for word, scores in tf_scores.items():
    print(f"{word}: {scores}")



# def compute_idf(docs):
#     idf_scores = defaultdict(lambda: 0)
#     total_docs = len(docs)
#     all_tokens_set = set([item for sublist in docs for item in sublist])

#     for token in all_tokens_set:
#         contains_token = sum(1 for doc in docs if token in doc)
#         idf_scores[token] = math.log(total_docs / (1 + contains_token))
    
#     return idf_scores

# idf_scores = compute_idf(data)


# def compute_tfidf(tf_scores, idf_scores):
#     tfidf_scores = []
#     for tf_doc in tf_scores:
#         tfidf_doc = {}
#         for token in tf_doc:
#             tfidf_doc[token] = tf_doc[token] * idf_scores[token]
#         tfidf_scores.append(tfidf_doc)
#     return tfidf_scores

# tfidf_scores = compute_tfidf(tf_scores, idf_scores)


# def save_tfidf_to_csv(tfidf_scores, filename='tfidf_output.csv'):
#     with open(filename, mode='w', newline='', encoding='utf-8') as file:
#         writer = csv.writer(file, delimiter=';')
#         for doc_index, tfidf_doc in enumerate(tfidf_scores):
#             for word, score in tfidf_doc.items():
#                 writer.writerow([doc_index, word, score])

# save_tfidf_to_csv(tfidf_scores)
