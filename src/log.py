import logging
6
def setup_logger(name, log_file, level=logging.INFO):
    path = './logs/'
    handler = logging.FileHandler(path+log_file)    
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    handler.setFormatter(formatter)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    
    return logger