from generate_inv_list import create_inverted_index, csv_to_dict, dict_list_to_csv, parse_xml_to_structured_data
from indexer import compute_tf_idf, dict_dict_to_csv, process_idf, process_term_frequencies, csv_to_dict_list
import pandas as pd 


xml_path = './data/cfquery.xml'
dtd_path = './data/cfcquery-2.dtd'
path = './data/'
datas_list_path = ['cf74.xml', 'cf75.xml', 'cf76.xml', 'cf77.xml',   'cf78.xml', 'cf79.xml']
# datas_list_path = ['cf79.xml']
#01154
df_data = pd.DataFrame(columns=['RecordNum', 'Abstract'])
records = {}
for file in  datas_list_path:
    data_path = path + file
    records = parse_xml_to_structured_data(records, data_path)

inverted_index = create_inverted_index(records)
path_inv_list = './data/inv_list.csv'
dict_list_to_csv(inverted_index, path_inv_list)

data = csv_to_dict_list(path_inv_list)
N = len(data)
tf_per_tokens_and_docs = process_term_frequencies(data, N)
idf_per_tokens_and_docs = process_idf(tf_per_tokens_and_docs, N)
tfidf = compute_tf_idf(tf_per_tokens_and_docs, idf_per_tokens_and_docs)
headers = ['token', 'doc_id', 'tfidf']
dict_dict_to_csv(tfidf, path+'tfidf.csv', headers)
# SALIVARI;['2: 0.12543137291905748', '32: 0.10273426734322803', '77: 0.17978496785064907', '137: 0.026438965860389567',