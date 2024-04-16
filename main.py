from log import setup_logger
import configuration


log = setup_logger()

def main():
    # Configura o logger
    logger = log.setup_logger()

    # Lê as configurações
    config = configuration.read('path/to/your/PC.CFG')
    print(config)

if __name__ == "__main__":
    main()