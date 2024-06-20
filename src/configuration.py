import os
import time
import log


def check_file_exists(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"O arquivo {file_path} não foi encontrado.")
    return True


def read_and_process_config(file_path):
    config = {}
    with open(file_path, 'r') as file:
        for line in file:
            key, value = line.strip().split('=')
            config[key.lower()] = value.replace('>', '').replace('<', '')
    return config


def log_duration_and_success(start_time, logger):
    elapsed_time = time.time() - start_time
    logger.info(f"Arquivo de configuracao lido com sucesso em {elapsed_time:.2f} segundos.")


def read(config_path, logger): 
    try:
        logger.info(f"Iniciando a leitura do arquivo de configuracao {config_path}")
        start_time = time.time()
        check_file_exists(config_path)
        config = read_and_process_config(config_path)
        log_duration_and_success(start_time, logger)

    except FileNotFoundError as e:
        logger.error(f"Erro: {e}")
        raise
    except Exception as e:
        logger.error(f"Erro ao processar o arquivo de configuracao: {e}")
        raise

    return config