import configparser
import requests
import logging
from elasticsearch import Elasticsearch


# Logger config
logging.basicConfig(filename='github_fetcher.log', format='%(asctime)s %(levelname)s {%(module)s} [%(funcName)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)
logger = logging.getLogger(__name__)


def get_config(env):
    """Get configurations based on the key
    """
    logger.info(f"Fetching config details related to - {env}..")
    config = configparser.ConfigParser()
    with open('config.ini') as f:
        config.read_file(f)
    return(config._sections[env])


def get_github_punch_card_data():
    github_config = get_config('GITHUB')
    url = github_config['endpoint']+github_config['punch_card_rsrc']
    logger.info(f'Firing the GET call - {url}')
    return requests.get(url)
    

if __name__ == '__main__':
    response = get_github_punch_card_data()
    if response.status_code == 200:
        response.json()
    else:
        logger.warn("Failed fetching punch card details!")