import logging
import time

def setup_logger():
    # Cria um logger
    logger = logging.getLogger('InformationRetrievalSystem')
    logger.setLevel(logging.DEBUG)  # Pode capturar todos os níveis de logs

    # Cria um file handler que loga até mesmo mensagens de debug
    fh = logging.FileHandler('data/information_retrieval_system.log')
    fh.setLevel(logging.DEBUG)

    # Cria um formatter e adiciona ao handler
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)

    # Adiciona o handler ao logger
    logger.addHandler(fh)

    return logger

# Configura o logger

