import math
import time
from configuration import read
from manager import  csv_to_dict_list, dict_dict_to_csv
import log


def calculate_frequencies_per_tokens(data):
    freq_per_tokens = {}
    for token, doc_list in data.items():
        if token not in freq_per_tokens:
            freq_per_tokens[token] = {}
        for doc_id in doc_list:
            if doc_id in freq_per_tokens[token]:
                freq_per_tokens[token][doc_id] += 1
            else:
                freq_per_tokens[token][doc_id] = 1
    return freq_per_tokens


def calculate_max_frequencies(freq_per_tokens):
    max_freq_per_doc = {}
    for _, doc_freq in freq_per_tokens.items():
        for doc_id, freq in doc_freq.items():
            if doc_id not in max_freq_per_doc:
                max_freq_per_doc[doc_id] = freq
            else:
                max_freq_per_doc[doc_id] = max(max_freq_per_doc[doc_id], freq)
    return max_freq_per_doc


def compute_tf(frequencies_per_tokens, max_frequencies):
    for token, freq_list in frequencies_per_tokens.items():
        for doc_id, freq in freq_list.items():
            frequencies_per_tokens[token][doc_id] = float(freq) / float(max_frequencies[doc_id])
    return frequencies_per_tokens
 

def process_term_frequencies(data):
    freq_per_tokens = calculate_frequencies_per_tokens(data)
    max_freq_per_doc = calculate_max_frequencies(freq_per_tokens)
    tf_scores = compute_tf(freq_per_tokens, max_freq_per_doc)
    return tf_scores


def idf(N:int, nt:int):
    return math.log10((N+1) / ((nt+1)+1))


def process_idf(freq_per_tokens, N):
    idf_per_tokens_and_docs = {}
    for token, docs in freq_per_tokens.items():
        nt = len(docs)
        idf_score = idf(N, nt)
        idf_per_tokens_and_docs[token] = {doc_id: idf_score for doc_id in docs}
    return idf_per_tokens_and_docs


def compute_tf_idf(tf_per_tokens_and_docs, idf_per_tokens_and_docs):
    tf_idf_scores = {}
    for token, doc_freqs in tf_per_tokens_and_docs.items():
        tf_idf_scores[token] = {}
        for doc_id, tf_score in doc_freqs.items():
            idf_score = idf_per_tokens_and_docs[token][doc_id]
            tf_idf_scores[token][doc_id] = tf_score * idf_score
    return tf_idf_scores


def main():
    logger = log.setup_logger('index', 'index.log')
    logger.info("Inicio do indexador")

    start_time = time.time()
    path = './data/'
    config = read('./instructions/INDEX.CFG', logger)
    data = csv_to_dict_list(path+config['leia'])
    logger.info("Arquivo lido {0}.".format(config['leia']))

    N = len(data)

    tf_per_tokens_and_docs = process_term_frequencies(data)
    idf_per_tokens_and_docs = process_idf(tf_per_tokens_and_docs, N)
    tfidf = compute_tf_idf(tf_per_tokens_and_docs, idf_per_tokens_and_docs)
    headers = ['token', 'doc_id', 'tfidf']
    dict_dict_to_csv(tfidf, path+config['escreva'], headers)
    logger.info("TFIDF processados e salvos em {0}.".format(config['escreva']))
    logger.info("Indexador finalizado em {:.2f} segundos.".format(time.time() - start_time))


if __name__ == "__main__":
    main()
