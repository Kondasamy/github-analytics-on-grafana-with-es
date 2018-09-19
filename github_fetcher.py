import configparser
import requests
import logging
from elasticsearch import Elasticsearch


# Logger config
logging.basicConfig(filename='github_fetcher.log', format='%(asctime)s %(levelname)s {%(module)s} [%(funcName)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)
logger = logging.getLogger(__name__)


def get_config(env):
    """Get configurations based on the key
    :param env: String value to identify config type
    :returns : Dictionary of config values
    """
    logger.info(f"Fetching config details related to - {env}..")
    config = configparser.ConfigParser()
    with open('config.ini') as f:
        config.read_file(f)
    return(config._sections[env])


def get_github_punch_card_data():
    """Get Github - number of commits per hour in each day
    """
    github_config = get_config('GITHUB')
    repo_config = get_config('REPOS')
    auth_headers = {'Authorization': github_config['api_key'],'Content-Type': 'application/json'}
    for key, value in repo_config.items():
        print(f'Fetching results for the repo : {key}')
        url = github_config['endpoint'] + repo_config[key] + github_config['punch_card_rsrc']
        print(f'Firing the GET call - {url}')
        requests.get(url, auth_headers)
    

if __name__ == '__main__':
    get_github_punch_card_data()
    # if response.status_code == 200:
    #     print(response.json())
    # else:
    #     logger.warn("Failed fetching punch card details!")