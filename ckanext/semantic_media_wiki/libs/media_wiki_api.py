from datetime import datetime
import logging

import requests
from mwclient import Site
from mwclient.errors import MwClientError

log = logging.getLogger(__name__)


def read_credentials(credentials_path):
    if not credentials_path:
        return None, None

    credentials = {}
    with open(credentials_path, 'r') as credentials_file:
        for line in credentials_file:
            if '=' not in line:
                continue
            key, value = line.strip().split('=', 1)
            credentials[key.strip().lower()] = value.strip()

    return credentials.get('username'), credentials.get('password')


class API():
    
    username = None
    password = None
    site = None
    host = ""
    path = "/wiki/"
    scheme = "https"
    query = ""
    target_sfb = ""
    image_field = ""
    timeout = 30


    def __init__(
            self, username, password, query, host, target_sfb,
            sample_query=False, path=None, scheme="https", timeout=30):
        self.username = username
        self.password = password
        self.query = query
        self.host = host
        self.path = path or "/wiki/"
        self.scheme = scheme or "https"
        self.timeout = timeout
        self.sample_query = sample_query
        self.target_sfb = target_sfb
        if self.target_sfb == "1153":
            self.image_field = "Image"
        else:
            self.image_field = "depiction"


    def pipeline(self, offset=0, limit=9999999):
        results = []
        machines_imageUrl = {}
        try:
            self.login(self.host, self.path, self.scheme)
            paged_query = f"{self.query}|limit={limit}|offset={offset}"

            data = self.site.raw_api(
                "ask",
                query=paged_query,
                format="json"
            )

            smw_results = data.get("query", {}).get("results", {})

            for _, answer in smw_results.items():
                if (not self.sample_query) and answer and answer.get("printouts"):
                    processed_answer = self.unpack_ask_response(answer)
                    results.append(processed_answer)

                    if self.image_field in processed_answer:
                        depiction_page = processed_answer[self.image_field]
                        depiction_url = self.mw_getfile_url(filepage=depiction_page)
                        machines_imageUrl[processed_answer["page"]] = depiction_url

                elif self.sample_query:
                    answer_unpacked = self.unpack_ask_response(answer)
                    results.append(answer_unpacked)
            return [results, machines_imageUrl]

        except (MwClientError, requests.exceptions.RequestException,
                KeyError, TypeError, ValueError) as exc:
            log.warning("Semantic MediaWiki API request failed: %s", exc)
            return [[], {}]

    def login(self, host: str, path: str, scheme: str):
        site_ = Site(
            host=host,
            path=path,
            scheme=scheme,
            reqs={'timeout': self.timeout},
        )
        if self.username and self.password:
            site_.login(username=self.username, password=self.password)        
        self.site = site_
        return True
    

    def unpack_ask_response(self, response):
        results = {}
        printouts = response['printouts']
        page = response['fulltext']
        results['page'] = page
        for prop in printouts:
            p_item = response['printouts'][prop]
            for prop_val in p_item:
                if isinstance(prop_val, dict) is False:
                    results[prop] = prop_val
                else:                   
                    props = list(prop_val.keys())
                    if 'fulltext' in props:
                        val = prop_val.get('fulltext')
                    elif 'timestamp' in props:
                        val = datetime.fromtimestamp(
                            int(prop_val.get('timestamp')))
                    else:
                        val = list(prop_val.values())[0]
                    results[prop] = val
        return results

    
    def mw_getfile_url(self, filepage):
        filepage = filepage.replace('File:', '')
        try:
            imageinfo = self.site.images[filepage].imageinfo
            if 'url' in imageinfo.keys():
                return imageinfo['url']
        except (MwClientError, requests.exceptions.RequestException,
                KeyError, TypeError) as exc:
            log.warning("Semantic MediaWiki image lookup failed: %s", exc)
        return ""
