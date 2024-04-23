import csv
import math

def csv_to_dict_list(filename):
    data_dict = {}
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        for row in reader:
            key = row[0]
            values = row[1].strip('[]').split(',')
            values = list(map(str, values))
            data_dict[key] = values
    return data_dict


def dict_dict_to_csv(data, file_path, headers):
    with open(file_path, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow(headers)
        
        for outer_key, inner_dict in data.items():
            for inner_key, value in inner_dict.items():
                inner_key = inner_key.strip(" '")
                writer.writerow([outer_key, inner_key, value])


def add_dict(d:dict, key:str, value:int):
    if (key not in d):
        d[key] = 0
    d[key] += value


def add_dict_dict(d:dict, key:str):
    if (key not in d):
        d[key] = {}


def max_dict(dmax:dict, d:dict, key:str):
    if (key not in dmax):
        dmax[key] = 0
    dmax[key] = max(dmax[key], d[key])


def calculate_frequencies_per_tokens(data):
    freq_per_tokens = {}
    for token, freq_list in data.items():
        add_dict_dict(freq_per_tokens, token)
        for doc_id in freq_list:
            add_dict(freq_per_tokens[token], doc_id, 1) 
    return freq_per_tokens


def calculate_max_frequencies(data):
    max_freq_per_tokens = {}
    for token, doc_freq in data.items():
        for doc_id, freq in doc_freq.items():
            max_dict(max_freq_per_tokens, data[token], doc_id)
    return max_freq_per_tokens


def compute_tf(frequencies_per_tokens, max_frequencies):
    for token, freq_list in frequencies_per_tokens.items():
        for doc_id, freq in freq_list.items():
            frequencies_per_tokens[token][doc_id] = freq / max_frequencies.get(doc_id, 1)
    return frequencies_per_tokens
 

def process_term_frequencies(data, N:int):
    freq_per_tokens = calculate_frequencies_per_tokens(data)
    return compute_tf(freq_per_tokens, calculate_max_frequencies(freq_per_tokens))


def idf(N:int, nt:int):
    return math.log(N / nt)


def process_idf(freq_per_tokens, N:int):
    idf_per_tokens_and_docs = freq_per_tokens
    for token in freq_per_tokens.keys():
        nt = len(freq_per_tokens[token].keys())
        for doc_id in freq_per_tokens[token].keys():
            idf_per_tokens_and_docs[token][doc_id] = idf(N, nt)
    return idf_per_tokens_and_docs


def compute_tf_idf(tf_per_tokens_and_docs, idf_per_tokens_and_docs):
    for token in tf_per_tokens_and_docs.keys():
        for doc_id in tf_per_tokens_and_docs[token].keys():
            tf = tf_per_tokens_and_docs[token][doc_id]
            idf = idf_per_tokens_and_docs[token][doc_id]
            tf_per_tokens_and_docs[token][doc_id] = tf * idf
    return tf_per_tokens_and_docs