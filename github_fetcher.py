import configparser
import requests
import logging
import uuid
from datetime import datetime, date, time
from elasticsearch import Elasticsearch, helpers, RequestError


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
        url = github_config['endpoint'] + value + github_config['punch_card_rsrc']
        print(f'Firing the GET call - {url}')
        response = requests.get(url, auth_headers)
        if response.status_code == 200:
            process_punch_data_for_es(key, response.json())
        else:
            logger.warn(f"Failed attempt with status code : {response.status_code}")


def process_punch_data_for_es(key, response):
    """Structurize punch card data 
    """
    # Elastic search connection
    es_config = get_config('ELASTICSEARCH')
    _es = Elasticsearch([{'host': es_config['host'], 'port': int(es_config['port'])}])

    today = int(datetime.combine(date.today(), time(0, 0, 0)).timestamp()) # unix timestamp
    past_eigth_day = today - (86400*8) # 8 days * 86400 seconds
        
    if _es.ping():
        # Setting the mapping of elasticsearch index
        if not _es.indices.exists(es_config['index']):
            mapping = '''
            {
                "mappings": {
                    "punch_card": {
                        "properties": {
                            "commits": {
                                "type": "long"
                            },
                            "repo": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                    }
                                }
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
            _es.indices.create(index=es_config['index'], body= mapping)

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
                _es.index(index=es_config['index'], doc_type='punch_card', id=f"{key}_{timestamp}", body=data)
            except RequestError as re:
                print(re.info)
                   
    else:
        logger.warn("Failed attempt connecting elasticsearch instance")


if __name__ == '__main__':
    print(get_config('REPOS')) # 1537284600
    get_github_punch_card_data()