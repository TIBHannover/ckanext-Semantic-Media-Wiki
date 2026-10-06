from pprint import pprint
from mwclient import Site
from datetime import datetime
import logging
from urllib import parse
log = logging.getLogger(__name__)

class API():
    
    username = None
    password = None
    site = None
    host = ""
    query = ""
    target_sfb = ""
    image_field = ""


    def __init__(
        self,
        username,
        password,
        query,
        host,
        target_sfb,
        sample_query=False,
        path=None,
        scheme="https",
    ):
        self.username = username
        self.password = password
        self.query = query
        self.host = host
        self.sample_query = sample_query
        self.target_sfb = str(target_sfb or "").strip()
        self.path = path or self.default_path(self.target_sfb)
        self.scheme = scheme or "https"
        if self.target_sfb == "1153":
            self.image_field = "Image"
        else:
            self.image_field = "depiction"

    @staticmethod
    def default_path(target_sfb):
        paths = {
            "1153": "/wiki-sfb1153/",
            "1368": "/wiki-sfb1368/",
        }
        try:
            return paths[target_sfb]
        except KeyError:
            raise ValueError(
                "ckanext.smw.mediawiki.api.path must be configured "
                "for project {}".format(target_sfb or "<unset>")
            )


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

            existing_pages = self.pages_exist(
                answer.get("fulltext")
                for answer in smw_results.values()
                if answer and answer.get("fulltext")
            )

            for _, answer in smw_results.items():
                # ----- MODE A: normal behavior (not sample_query) -----
                if (not self.sample_query) and answer and answer.get("printouts"):
                    processed_answer = self.unpack_ask_response(answer)
                    processed_answer["exists"] = existing_pages.get(
                        processed_answer["page"], False
                    )
                    results.append(processed_answer)

                    if self.image_field in processed_answer:
                        depiction_page = processed_answer[self.image_field]
                        depiction_url = self.mw_getfile_url(filepage=depiction_page)
                        machines_imageUrl[processed_answer["page"]] = depiction_url

                # ----- MODE B: sample_query behavior -----
                elif self.sample_query:
                    answer_unpacked = self.unpack_ask_response(answer)
                    answer_unpacked["exists"] = existing_pages.get(
                        answer_unpacked["page"], False
                    )
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

    def pages_exist(self, titles):
        """Return existence flags using batched, authenticated API requests."""
        titles = list(dict.fromkeys(title for title in titles if title))
        existence = {title: False for title in titles}

        for offset in range(0, len(titles), 50):
            chunk = titles[offset:offset + 50]
            try:
                data = self.site.raw_api(
                    "query",
                    prop="info",
                    titles="|".join(chunk),
                    redirects=1,
                    format="json",
                    formatversion=2,
                )
            except Exception:
                log.exception("Could not check whether SMW pages exist")
                continue
            query = data.get("query", {})
            aliases = {title: title for title in chunk}
            for item in query.get("normalized", []):
                aliases[item["from"]] = item["to"]
            for item in query.get("redirects", []):
                aliases[item["from"]] = item["to"]

            returned = {
                page.get("title"): "missing" not in page
                for page in query.get("pages", [])
            }
            for title in chunk:
                resolved = aliases.get(title, title)
                resolved = aliases.get(resolved, resolved)
                existence[title] = returned.get(resolved, False)

        return existence

    def urls_exist(self, urls, base_url):
        """Validate SMW page URLs while leaving unrelated external URLs alone."""
        urls = list(dict.fromkeys(url for url in urls if url))
        base = parse.urlsplit(base_url)
        base_path = base.path.rstrip("/") + "/"
        url_titles = {}
        for url in urls:
            parsed = parse.urlsplit(url)
            if (
                parsed.scheme != base.scheme
                or parsed.netloc != base.netloc
                or not parsed.path.startswith(base_path)
            ):
                continue
            title = parse.unquote(parsed.path[len(base_path):]).replace("_", " ")
            if title:
                url_titles[url] = title

        existence = self.pages_exist(list(url_titles.values()))
        return {
            url: existence.get(url_titles[url], False) if url in url_titles else True
            for url in urls
        }
    

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
