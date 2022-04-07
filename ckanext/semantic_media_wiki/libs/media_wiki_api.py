from pprint import pprint
from mwclient import Site
from datetime import datetime

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
    

    def pipeline(self):
        results = []
        machines_imageUrl = {}
        self.login(self.host, self.path, self.scheme)
        try:            
            self.login(self.host, self.path, self.scheme)
            raw_results = self.site.ask(self.query)                            
            for answer in raw_results:
                if not self.sample_query and answer and answer['printouts']:
                    processed_answer = self.unpack_ask_response(answer) 
                    results.append(processed_answer)                
                    if self.image_field in processed_answer.keys():
                        depiction_page =  processed_answer[self.image_field]
                        depiction_url = self.mw_getfile_url(filepage=depiction_page)                                        
                        machines_imageUrl[processed_answer['page']] = depiction_url

                elif self.sample_query:
                    answer_unpacked = self.unpack_ask_response(answer)
                    results.append(answer_unpacked)


        except:
            return [[], {}]
            
        return [results, machines_imageUrl]


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