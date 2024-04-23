import re
import time
import log
import xml.etree.ElementTree as ET
import nltk
from nltk.corpus import stopwords

from manager import append_dict_list, dict_list_to_csv
from processor import generate_csv, validate_xml

# import nltk

# nltk.download('stopwords')
# nltk.download('punkt')
stop_words = stopwords.words('english')
stop_words.extend(["et", "al"])

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
        record_num = record.find('.//RECORDNUM').text
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

def process_cf(xml_path, dtd_path, path):
    logger = log.setup_logger()
    try:
        logger.info("Processando cf.") #TODO: Ajeitar pra printar cada arquivo processado
        start_time = time.time()
        if validate_xml(xml_path, dtd_path):
            data = parse_xml_to_structured_data(xml_path)

            generate_csv(data, path + 'cf.csv') #TODO: Ajeitar pra colocar o nome de cada arquivo processado
        logger.info("Cf processado com sucesso em {:.2f} segundos.".format(time.time() - start_time))
    except Exception as e:
        logger.error(f"Erro ao processar cf: {e}")


def create_inverted_index(docs:dict):
    inverted_index = {}
    for doc_id, tokens in docs.items():
        inverted_index = process_words(inverted_index, tokens, doc_id)    
    return inverted_index


def inv_list(docs, path):
    #TODO: Add Log
    inverted_index = create_inverted_index(docs)
    dict_list_to_csv(inverted_index, path)
    return inverted_index