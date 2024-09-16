from ..utils.logger import logger

def handle_error(error):
    logger.error(f"An error occurred: {str(error)}")
    return "I'm sorry, but an error occurred. Can you please try again?"