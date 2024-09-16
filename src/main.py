from src.assistant.athena import Athena
from src.config import Config

def main():
    config = Config()
    athena = Athena(config)
    athena.run()

if __name__ == "__main__":
    main()