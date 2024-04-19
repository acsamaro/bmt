import time
from lxml import etree
import xml.etree.ElementTree as ET
import pandas as pd
import log

def generate_csv(data, output_path):
    data.to_csv(output_path, sep=';', index=False, header=True)

def validate_xml(xml_path, dtd_path):
    with open(dtd_path, 'rb') as f:
        dtd = etree.DTD(f)

    with open(xml_path, 'rb') as f:
        xml_doc = etree.parse(f)

    is_valid = dtd.validate(xml_doc)

    if is_valid:
        print("The XML is valid according to the DTD.")
    else:
        print("Validation failed:", dtd.error_log.filter_from_errors())

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

def process_queries(xml_path, dtd_path, path):
    logger = log.setup_logger()
    try:
        logger.info("Processando consultas.")
        start_time = time.time()
        if validate_xml(xml_path, dtd_path):
            df_consultas, df_esperados = process_query_file(xml_path)

            generate_csv(df_consultas, path + 'consultas.csv')
            generate_csv(df_esperados, path + 'esperados.csv')
        logger.info("Consultas processadas com sucesso em {:.2f} segundos.".format(time.time() - start_time))
    except Exception as e:
        logger.error(f"Erro ao processar consultas: {e}")

def parse_xml_to_structured_data(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    records = []

    for record in root.findall('.//RECORD'):
        record_num = record.find('.//RECORDNUM').text if record.find('.//RECORDNUM') is not None else ''
        summary = record.find('.//ABSTRACT') if record.find('.//ABSTRACT') is not None else record.find('.//EXTRACT')
        abstract = summary.text.strip() if summary is not None else ''
        
        record_data = {
            'Record Number': record_num,
            'Abstract': abstract,
        }
        records.append(record_data)
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


#TODO: apagar os testes
xml_path = './data/cfquery.xml'
dtd_path = './data/cfcquery-2.dtd'
path = './data/'
data = parse_xml_to_structured_data('./data/cf77.xml')
print(data)