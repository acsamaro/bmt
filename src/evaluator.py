import logging
import pandas as pd
from collections import defaultdict
import matplotlib.pyplot as plt
from nltk.metrics import precision, recall, f_measure
import math
import numpy as np



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

        subset.loc[:,'Precision'] = subset['CumulativeRelevantRetrieved'] / subset['CumulativeRetrieved']
        subset.loc[:, 'Recall'] = subset['CumulativeRelevantRetrieved'] / total_relevant

        precision_recall[query] = subset[['Precision', 'Recall']]

    return precision_recall

def interpolate_precision_recall(precision_recall, recall_levels):
    interpolated_precision = {}

    for query, data in precision_recall.items():
        interp_precision = []
        for level in recall_levels:
            max_precision = data[data['Recall'] >= level]['Precision'].max()
            if pd.isna(max_precision):
                max_precision = 0
            interp_precision.append(max_precision)
        interpolated_precision[query] = interp_precision

    return interpolated_precision, recall_levels


def dict_to_df(d:dict):
    data = pd.DataFrame()
    for query_data in d.values():
        data = pd.concat([data, query_data], ignore_index=True)

    return data

def interpolate_precision_recall(precision_recall, recall_levels):
    df_precision_recall = dict_to_df(precision_recall)
    df_precision_recall = df_precision_recall.sort_values(by='Recall', ascending=False)
    interp_precision = []
    max_precision = 0
    for level in reversed(recall_levels):
        current_max_precision = df_precision_recall[df_precision_recall['Recall'] >= level]['Precision'].max(skipna=True)
        max_precision = max(max_precision, current_max_precision if pd.notna(current_max_precision) else 0)
        interp_precision.insert(0, max_precision)  # Insere no início para manter a ordem crescente dos recalls

    return interp_precision, recall_levels



def plot_precision_recall(precision_recall_data):
    # Unpack the precision values and recall levels
    interpolated_precision, recall_levels = precision_recall_data

    # Create a plot
    plt.figure(figsize=(8, 6))
    plt.plot(recall_levels, interpolated_precision, marker='o', linestyle='-', color='blue', label='Interpolated Precision')
    
    plt.title('11-Point Precision and Recall Curve')
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.grid(True)
    plt.xticks(recall_levels, labels=[f'{x:.1f}' for x in recall_levels])
    plt.yticks(np.linspace(0, 1, 11), labels=[f'{y:.1f}' for y in np.linspace(0, 1, 11)])
    plt.legend()
    plt.show()


def main():
    result_path = './results/resultados.csv'
    result_columns_name = ['query_id', 'rank', 'doc_id', 'similarity']
    df_results = read_csv_with_custom_columns(result_path, result_columns_name)

    expected_path = './results/esperados.csv'
    expected_columns_name = ['query_id', 'doc_id', 'votes']
    df_expected = read_csv_with_custom_columns(expected_path, expected_columns_name)

    df_results['doc_id'] = df_results['doc_id'].str.replace("'", "").astype(int)
    df_expected['doc_id'] = df_expected['doc_id'].astype(int)
  
    precision_recall = compute_precision_recall_vectorized(df_results, df_expected)
    print(precision_recall)
    recall_levels = np.linspace(0, 1, 11)
    interpolated_precision = interpolate_precision_recall(precision_recall, recall_levels)
    plot_precision_recall(interpolated_precision)

    
    # Further plotting or analysis can be done with interpolated_precision and recall_levels

if __name__ == "__main__":
    main()
 