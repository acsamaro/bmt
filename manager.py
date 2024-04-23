from collections import defaultdict
import csv

def csv_to_dict(file_path, key_name, value_name):
    d = {}
    with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        next(reader)
        for row in reader:
            key = row[key_name].strip()
            value = row[value_name].strip()
            d[key] = value
    return d


def append_dict_list(d:dict, key:str, value:int):
    if (key not in d):
        d[key] = []
    d[key].append(value)


def dict_list_to_csv(d: dict, path:str):
     with open(path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for key, value in d.items():
                writer.writerow([key.upper(), str(value)])


def csv_to_dict_list(filename):
    data_dict = {}
    with open(filename, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        for row in reader:
            key = row[0]
            values = row[1].strip('[]').split(',')
            values = list(map(str, values))
            data_dict[key] = values
    return data_dict


def dict_dict_to_csv(tfidf, filepath, headers):
    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow(headers)
        for token, docs in tfidf.items():
            for doc_id, tfidf_value in docs.items():
                # Formata o TF-IDF para mostrar até 6 casas decimais
                formatted_tfidf = f"{tfidf_value:.6f}"
                writer.writerow([token, doc_id, formatted_tfidf])

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

