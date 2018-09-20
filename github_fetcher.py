import configparser
import requests
import logging
from datetime import datetime, date, time
from elasticsearch import Elasticsearch, helpers, RequestError


# Logger config
logging.basicConfig(filename='github_fetcher.log', format='%(asctime)s %(levelname)s {%(module)s} [%(funcName)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.WARN)
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
    GITHUB API <GET /repos/:owner/:repo/stats/punch_card>
    """
    github_config = get_config('GITHUB')
    repo_config = get_config('REPOS')
    auth_headers = {'Authorization': github_config['api_key'],'Content-Type': 'application/json'}
    for key, value in repo_config.items():
        logger.info(f'Fetching results for the repo : {key}')
        url = github_config['endpoint'] + value + github_config['punch_card_rsrc']
        logger.info(f'Firing the GET call - {url}')
        response = requests.get(url, auth_headers)
        if response.status_code == 200:
            process_punch_data_for_es(key, response.json())
        else:
            logger.warn(f"Failed attempt with status code : {response.status_code}")


def process_punch_data_for_es(key, response):
    """Structurize punch card data
    :param key: Denotes the repo name fetched from config file
    :param response: JSON parsed Response of punch data
    """
    # Elastic search connection
    es_config = get_config('ELASTICSEARCH')
    _es = Elasticsearch([{'host': es_config['host'], 'port': int(es_config['port'])}])

    today = int(datetime.combine(date.today(), time(0, 0, 0)).timestamp()) # unix timestamp
    past_eigth_day = today - (86400*8) # 8 days * 86400 seconds
        
    if _es.ping():
        # Setting the mapping of elasticsearch index
        if not _es.indices.exists(es_config['main_index']):
            mapping = '''
            {
                "mappings": {
                    "punch_card": {
                        "properties": {
                            "commits": {
                                "type": "long"
                            },
                            "repo": {
                                "type": "keyword"
                            },
                            "timestamp": {
                                "type": "date",
                                "format": "epoch_second"
                            }
                        }
                    }
                }
            }
            '''
            _es.indices.create(index=es_config['main_index'], body= mapping)

        # Process and populate data to Elasticsearch
        for hour in response:
            timestamp = past_eigth_day+3600
            past_eigth_day = timestamp
            data = {
                    'repo': key,
                    'commits': hour[2],
                    'timestamp': timestamp
                }
            try:
                _es.index(index=es_config['main_index'], doc_type='punch_card', id=f"{key}_{timestamp}", body=data)
            except RequestError as re:
                logger.info(re.info)
    else:
        logger.warn("Failed attempt connecting elasticsearch instance")


def get_github_contributors_data():
    """For a Github repo - Get contributors list with additions, deletions, and commit counts
    GITHUB API <GET /repos/:owner/:repo/stats/contributors>
    """
    github_config = get_config('GITHUB')
    repo_config = get_config('REPOS')
    auth_headers = {'Authorization': github_config['api_key'],'Content-Type': 'application/json'}
    for key, value in repo_config.items():
        logger.info(f'Fetching results for the repo : {key}')
        url = github_config['endpoint'] + value + github_config['contrib_rsrc']
        logger.info(f'Firing the GET call - {url}')
        response = requests.get(url, auth_headers)
        if response.status_code == 200:
            process_contrib_data_for_es(key, response.json())
        else:
            logger.warn(f"Failed attempt with status code : {response.status_code}")


def process_contrib_data_for_es(key, response):
    """Structurize github repo contributors data
    :param key: Denotes the repo name fetched from config file
    :param response: JSON parsed Response of contributors data
    """
    # Elastic search connection
    es_config = get_config('ELASTICSEARCH')
    _es = Elasticsearch([{'host': es_config['host'], 'port': int(es_config['port'])}])

    if _es.ping():
        # Setting the mapping of elasticsearch index
        if not _es.indices.exists(es_config['contrib_index']):
            mapping = '''
            {
                "mappings": {
                    "contribs": {
                        "properties": {
                            "repo": {
                                "type": "keyword"
                            },
                            "author": {
                                "type": "keyword"
                            },
                            "timestamp": {
                                "type": "date",
                                "format": "epoch_second"
                            },
                            "addition": {
                                "type": "long"
                            },
                            "deletion": {
                                "type": "long"
                            },
                            "commits": {
                                "type": "long"
                            }
                        }
                    }
                }
            }
            '''
            _es.indices.create(index=es_config['contrib_index'], body= mapping)

        # Process and populate data to Elasticsearch
        for contributor in response:
            author = contributor['author']['login']
            for week in contributor['weeks']:
                data = {
                    'repo': key,
                    'author': author,
                    'timestamp': week['w'],
                    'addition': week['a'],
                    'deletion': week['d'],
                    'commits': week['c'],
                }
                _es.index(index=es_config['contrib_index'], doc_type='contribs', id=f"{author}_{week['w']}", body=data)
    else:
        logger.warn("Failed attempt connecting elasticsearch instance")


if __name__ == '__main__':
    get_github_punch_card_data()
    get_github_contributors_data()
