import time
from lxml import etree
import xml.etree.ElementTree as ET
import pandas as pd
from configuration import read
import log
from nltk.corpus import stopwords

stop_words = set(stopwords.words('english'))

def validate_xml(xml_path, dtd_path, logger):
    with open(dtd_path, 'rb') as f:
        dtd = etree.DTD(f)

    with open(xml_path, 'rb') as f:
        xml_doc = etree.parse(f)

    is_valid = dtd.validate(xml_doc)

    if is_valid:
        logger.info("The XML is valid according to the DTD.")
    else:
        logger.info("Validation failed:", dtd.error_log.filter_from_errors())

    return is_valid

def process_query_file(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    data_queries = []
    data_results = []
    
    for query in root.findall(".//QUERY"):
        query_id = query.find("QueryNumber").text
        query_text = query.find("QueryText").text
        
        data_queries.append({
            'QueryID': query_id,
            'QueryText': query_text,
        })
        
        for record in query.findall(".//Records"):
            for item in record.findall(".//Item"):
                doc_id = item.text
                item_score = item.get('score')
                
                data_results.append({
                    'QueryID': query_id,
                    'DocNumber': doc_id,
                    'DocVotes': item_score
                })

    df_queries = pd.DataFrame(data_queries)
    df_results = pd.DataFrame(data_results)
    
    return df_queries, df_results

def process_queries(dtd_path, path):
    logger = log.setup_logger('process', 'process.log')
    try:
        start_time = time.time()
        config = read('./instructions/PC.CFG', logger)
        xml_path = config['leia']
        if validate_xml(path+xml_path, dtd_path, logger):
            logger.info("Processando consultas do arquivo {0}.".format(config['leia']))
            df_consultas, df_esperados = process_query_file(path+xml_path)
            df_consultas.to_csv(path + config['consultas'], sep=';', encoding='utf-8', index=False)
            df_esperados.to_csv(path + config['esperados'], sep=';', encoding='utf-8', index=False)
            logger.info("Numero de consultas processadas:{}".format(len(df_esperados)))
            logger.info("Arquivos gerados: {} e {}".format(path+config['consultas'], path+config['esperados']))
        logger.info("Processador finalizado em {:.2f} segundos.".format(time.time() - start_time))
    except Exception as e:
        logger.error(f"Erro ao processar consultas: {e}")

def main():
    path = './data/'
    dtd_path = path+'cfcquery-2.dtd'
    process_queries(dtd_path, path)



if __name__ == "__main__":
    main()