import re
import time
import xml.etree.ElementTree as ET
import nltk
from nltk.corpus import stopwords
from manager import append_dict_list, dict_list_to_csv
from processor import validate_xml
import time
import log

stop_words = stopwords.words('english')
stop_words.extend(["et", "al"])


def read_config(path):
    config = {'leia': [], 'escreva': None}
    with open(path, 'r') as file:
        for line in file:
            if line.startswith('LEIA'):
                config['leia'].append(line.strip().split('=')[1].replace('>', '').replace('<', ''))
            elif line.startswith('ESCREVA'):
                config['escreva'] = line.strip().split('=')[1].replace('>', '').replace('<', '')
    return config


def process_words(d:dict, words:list[str], doc_id:int):
    for word in words:
        append_dict_list(d, word, doc_id)
    return d

def tokenize(text:str):
    text = re.sub('[^a-zA-Z]+', ' ', text)    
    word_tokens = nltk.word_tokenize(text)
    tokens = [w.upper() for w in word_tokens if (not w.lower() in stop_words) and (len(w)>=2)]

    return tokens

def parse_xml_to_structured_data(records:dict, xml_path:str):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    for record in root.findall('.//RECORD'):
        record_num = record.find('.//RECORDNUM').text.strip()
        abstract = record.find('.//ABSTRACT')
        extract = record.find('.//EXTRACT')
        if abstract is not None:
            summary = abstract.text
        elif extract is not None:
            summary = extract.text
        else:
            continue  
        records[record_num] = tokenize(summary)
    return records


def create_inverted_index(docs:dict):
    inverted_index = {}
    for doc_id, tokens in docs.items():
        inverted_index = process_words(inverted_index, tokens, doc_id)    
    return inverted_index


def inv_list(docs, path):
    inverted_index = create_inverted_index(docs)
    dict_list_to_csv(inverted_index, path)
    return inverted_index


def process_cf(records, xml_path, dtd_path, logger):
    try:
        start_time = time.time()
        if validate_xml(xml_path, dtd_path, logger):
            records = parse_xml_to_structured_data(records, xml_path)
        logger.info(f"Arquivo processado em {time.time() - start_time:.2f} segundos.")
        return records
    except Exception as e:
        logger.error(f"Erro ao processar {xml_path}: {e}")


def main():
    logger = log.setup_logger('gli', 'gli.log')
    start_time = time.time()

    config_path = './instructions/GLI.CFG'
    path = './data/'
    config = read_config(config_path)
    output_path = './results/' + config['escreva']
    dtd_path = path + 'cfc-2.dtd'

    records = {}
    for file_name in config['leia']:
        logger.info("Processando o arquivo {0}.".format(file_name))
        xml_path = path + file_name
        records = process_cf(records, xml_path, dtd_path, logger)
    logger.info(f"Arquivos processados em {time.time() - start_time:.2f} segundos.")
    logger.info("Numero de documentos processads:{}".format(len(records.keys())))

    inverted_index = create_inverted_index(records)
    dict_list_to_csv(inverted_index, output_path)

    logger.info(f"Lista invertida salva em {config['escreva']}")
    logger.info(f"GLI finalizado em {time.time() - start_time:.2f} segundos.")



if __name__ == "__main__":
    main()

