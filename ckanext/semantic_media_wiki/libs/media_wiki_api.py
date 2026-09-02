from pprint import pprint
from mwclient import Site
from datetime import datetime
import logging
log = logging.getLogger(__name__)

class API():
    
    username = None
    password = None
    site = None
    host = ""
    path = "/wiki-sfb1153/"
    scheme = "https"
    query = ""
    target_sfb = ""
    image_field = ""


    def __init__(self, username, password, query, host, target_sfb, sample_query=False):
        self.username = username
        self.password = password
        self.query = query
        self.host = host
        self.sample_query = sample_query
        self.target_sfb = target_sfb
        if self.target_sfb == "1153":
            self.image_field = "Image"
        else:
            self.image_field = "depiction"


    def pipeline(self, offset=0, limit=9999999):
        results = []
        machines_imageUrl = {}
        self.login(self.host, self.path, self.scheme)
        try:
            # Build query (use self.query, not self.sample_query which is boolean!)
            paged_query = f"{self.query}|limit={limit}|offset={offset}"

            # SINGLE HTTP CALL (won’t auto-follow query-continue-offset)
            data = self.site.raw_api(
                "ask",
                query=paged_query,
                format="json"
            )

            smw_results = data.get("query", {}).get("results", {})  # dict: page_title -> answer_dict
            log.debug(smw_results.items())

            for _, answer in smw_results.items():
                # ----- MODE A: normal behavior (not sample_query) -----
                if (not self.sample_query) and answer and answer.get("printouts"):
                    processed_answer = self.unpack_ask_response(answer)
                    results.append(processed_answer)

                    if self.image_field in processed_answer:
                        depiction_page = processed_answer[self.image_field]
                        depiction_url = self.mw_getfile_url(filepage=depiction_page)
                        machines_imageUrl[processed_answer["page"]] = depiction_url

                # ----- MODE B: sample_query behavior -----
                elif self.sample_query:
                    answer_unpacked = self.unpack_ask_response(answer)
                    results.append(answer_unpacked)
            return [results, machines_imageUrl]

        except Exception:
            return [[], {}]

    def login(self, host: str, path: str, scheme: str):
        site_ = Site(host=host, path=path, scheme=scheme)
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
        f = self.site.images[filepage]
        imageinfo = f.imageinfo 
        file_url = ""
        if 'url' in imageinfo.keys():       
            file_url = imageinfo['url']
        return file_url