import logging
import time
import pandas as pd
from collections import defaultdict
import matplotlib.pyplot as plt
from nltk.metrics import precision, recall, f_measure
import math
import numpy as np

from configuration import log_duration_and_success, read
from log import setup_logger


def read_csv_with_custom_columns(file_path, column_names, separator=';'):
    return pd.read_csv(file_path, sep=separator, names=column_names, header=0)

def compute_precision_recall_vectorized(df_results, df_expected):
    df_merged = df_results.merge(df_expected, left_on=['query_id', 'doc_id'], right_on=['query_id', 'doc_id'], how='outer', indicator=True)
    df_merged['Relevant'] = (df_merged['_merge'] == 'both')
    df_merged['Retrieved'] = df_merged['doc_id'].notna()

    precision_recall = {}
    for query in df_merged['query_id'].unique():
        subset = df_merged[df_merged['query_id'] == query].copy()
        subset.loc[:, 'CumulativeRelevantRetrieved'] = subset['Relevant'].cumsum()
        subset.loc[:, 'CumulativeRetrieved'] = np.arange(1, len(subset) + 1)
        
        total_relevant = subset['Relevant'].sum()
        if total_relevant == 0:
            continue

        subset.loc[:,'Precision'] = subset['CumulativeRelevantRetrieved'] / subset['CumulativeRetrieved']
        subset.loc[:, 'Recall'] = subset['CumulativeRelevantRetrieved'] / total_relevant
        subset.loc[:, 'similarity'] = subset['similarity'].fillna(0)

        precision_recall[query] = subset[['Precision', 'Recall', 'Relevant', 'similarity']]

    return precision_recall

def interpolate_precision_recall(precision_recall, recall_levels):
    df_precision_recall = pd.DataFrame(columns=['Precision', 'Recall'])
    for query, data in precision_recall.items():
        if not data.empty and not data.isna().all().all():
            df_precision_recall = pd.concat([df_precision_recall, data], ignore_index=True)
    df_precision_recall = df_precision_recall.sort_values(by='Recall', ascending=False)
    
    interp_precision = []
    max_precision = 0
    for level in reversed(recall_levels):
        current_max_precision = df_precision_recall[df_precision_recall['Recall'] >= level]['Precision'].max(skipna=True)
        max_precision = max(max_precision, current_max_precision if pd.notna(current_max_precision) else 0)
        interp_precision.insert(0, max_precision)  # Insere no início para manter a ordem crescente dos recalls

    return interp_precision, recall_levels


def plot_precision_recall(precision_recall_data, save_path=None):
    interpolated_precision, recall_levels = precision_recall_data

    plt.figure(figsize=(8, 6))
    plt.plot(recall_levels, interpolated_precision, marker='o', linestyle='-', color='blue', label='Interpolated Precision')
    
    plt.title('11-Point Precision and Recall Curve')
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.grid(True)
    plt.xticks(recall_levels, labels=[f'{x:.1f}' for x in recall_levels])
    plt.yticks(np.linspace(0, 1, 11), labels=[f'{y:.1f}' for y in np.linspace(0, 1, 11)])
    plt.legend()
    if save_path:
        plt.savefig(save_path)
    plt.show()

def compute_f1_score(precision_recall):
    f1_scores = {}
    for query, data in precision_recall.items():
        data['F1'] = 2 * (data['Precision'] * data['Recall']) / (data['Precision'] + data['Recall']).replace(0, np.nan)
        f1_scores[query] = data['F1'].mean()  # Média do F1-Score para a consulta
    return f1_scores

def compute_precision_at_k(precision_recall, k):
    precision_at_k = {}
    for query, data in precision_recall.items():
        relevant_at_k = data['Relevant'][:k].sum()
        precision_at_k[query] = relevant_at_k / k
    return precision_at_k

def compute_r_precision(precision_recall):
    r_precision = {}
    for query, data in precision_recall.items():
        total_relevant = data['Relevant'].sum()
        if total_relevant > 0:
            relevant_at_r = data['Relevant'][:total_relevant].sum()
            r_precision[query] = relevant_at_r / total_relevant
        else:
            r_precision[query] = 0
    return r_precision

def plot_r_precision_histogram(r_precision, save_path=None):
    plt.figure(figsize=(8, 6))
    plt.hist(r_precision.values(), bins=10, edgecolor='black')
    plt.title('R-Precision Histogram')
    plt.xlabel('R-Precision')
    plt.ylabel('Frequency')
    plt.grid(True)
    if save_path:
        plt.savefig(save_path)
    plt.show()

def compute_map(precision_recall):
    average_precisions = []
    for query, data in precision_recall.items():
        precisions = data[data['Relevant']]['Precision']
        if len(precisions) > 0:
            average_precisions.append(precisions.mean())
    return np.mean(average_precisions)

def compute_mrr(precision_recall):
    reciprocal_ranks = []
    for query, data in precision_recall.items():
        relevant_indices = data[data['Relevant']].index
        if len(relevant_indices) > 0:
            first_relevant_rank = relevant_indices[0] + 1
            reciprocal_ranks.append(1 / first_relevant_rank)
    return np.mean(reciprocal_ranks)


def compute_dcg(scores, k):
    scores = np.asarray(scores)
    if scores.size == 0:
        return np.zeros(k)
    return np.cumsum(scores[:k] / np.log2(np.arange(2, k + 2)))

def compute_ndcg(scores, k):
    ideal_scores = sorted(scores, reverse=True)
    dcg = compute_dcg(scores, k)
    idcg = compute_dcg(ideal_scores, k)
    return dcg / idcg if idcg.all() != 0 else np.zeros(k)

def generate_f1_precision_csv(f1_scores, precision_at_5, precision_at_10, file_path):
    data = {
        'QueryID': list(f1_scores.keys()),
        'F1': list(f1_scores.values()),
        'Precision@5': [precision_at_5[qid] for qid in f1_scores.keys()],
        'Precision@10': [precision_at_10[qid] for qid in f1_scores.keys()]
    }
    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False, sep=';')

def generate_map_mrr_csv(map_score, mrr_score, file_path):
    data = {
        'Metric': ['MAP', 'MRR'],
        'Score': [map_score, mrr_score]
    }
    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False, sep=';')

def plot_dcg_ndcg(dcg, ndcg, k, save_path=None):
    ranks = np.arange(1, k + 1)
    plt.figure(figsize=(10, 6))
    plt.plot(ranks, dcg, marker='o', linestyle='-', color='blue', label='DCG')
    plt.plot(ranks, ndcg, marker='x', linestyle='--', color='green', label='nDCG')
    
    plt.title('DCG and nDCG up to Rank 10')
    plt.xlabel('Rank')
    plt.ylabel('Score')
    plt.xticks(ranks)
    plt.grid(True)
    plt.legend()
    if save_path:
        plt.savefig(save_path)
    plt.show()

def main():
    logger = setup_logger('evaluator', 'avalia.log')
    start_time = time.time()
    config = read('./instructions/AVALIA.CFG', logger)
    logger.info("Início da avaliação do modelo de RI")

    path = './results/'
    result_path = path + config['resultados'].split('.')[0] + '-' + config['stemmer'].upper() + '.' + config['resultados'].split('.')[1]
    result_columns_name = ['query_id', 'rank', 'doc_id', 'similarity']
    expected_path = path + config['esperados']
    expected_columns_name = ['query_id', 'doc_id', 'votes']

    logger.info("Lendo arquivos de resultados e esperados")
    df_results = read_csv_with_custom_columns(result_path, result_columns_name)
    df_expected = read_csv_with_custom_columns(expected_path, expected_columns_name)


    df_results['doc_id'] = df_results['doc_id'].str.replace("'", "").astype(int)
    df_expected['doc_id'] = df_expected['doc_id'].astype(int)
  
    logger.info("Calculando precisão e revocação")
    precision_recall = compute_precision_recall_vectorized(df_results, df_expected)
    recall_levels = np.linspace(0, 1, 11)
    interpolated_precision = interpolate_precision_recall(precision_recall, recall_levels)
    path_grafico_onze = path + config['graficoonze'].split('.')[0] + '-' + config['stemmer'].upper() + '.' + config['graficoonze'].split('.')[1]
    plot_precision_recall(interpolated_precision, save_path=path_grafico_onze)


    f1_scores = compute_f1_score(precision_recall)
    precision_at_5 = compute_precision_at_k(precision_recall, 5)
    precision_at_10 = compute_precision_at_k(precision_recall, 10)

    path_f1_precision = path + config['precisions'].split('.')[0] + '-' + config['stemmer'].upper() + '.' + config['precisions'].split('.')[1]
    generate_f1_precision_csv(f1_scores, precision_at_5, precision_at_10, path_f1_precision)

    r_precision = compute_r_precision(precision_recall)
    path_r_precision = path + config['rprecision'].split('.')[0] + '-' + config['stemmer'].upper() + '.' + config['rprecision'].split('.')[1]
    plot_r_precision_histogram(r_precision, save_path=path_r_precision)


    map_score = compute_map(precision_recall)
    mrr_score = compute_mrr(precision_recall)
    path_map_mrr = path + config['mapmrr'].split('.')[0] + '-' + config['stemmer'].upper() + '.' + config['mapmrr'].split('.')[1]
    generate_map_mrr_csv(map_score, mrr_score, path_map_mrr)


    all_scores = [data['similarity'].tolist() for data in precision_recall.values()]
    dcg_scores = np.mean([compute_dcg(scores, 10) for scores in all_scores], axis=0)
    ndcg_scores = np.mean([compute_ndcg(scores, 10) for scores in all_scores], axis=0)
    path_dcg_ndcg = path + config['dcgndcg'].split('.')[0] + '-' + config['stemmer'].upper() + '.' + config['dcgndcg'].split('.')[1]
    plot_dcg_ndcg(dcg_scores, ndcg_scores, 10, save_path=path_dcg_ndcg)


    logger.info("Fim da avaliação do modelo de RI")
    log_duration_and_success(start_time, logger)

if __name__ == "__main__":
    main()
