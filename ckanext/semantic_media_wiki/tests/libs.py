# encoding: utf-8

import ckan.plugins.toolkit as toolkit


class TestHelper():

    def get_api_config(sfb):
        if  sfb == "1153":
            credential_path = '/etc/ckan/default/credentials/smw1153.txt'
            smw_base_url = "https://smw.service.tib.eu/sfb1153/"
            api_host = "smw.service.tib.eu"
            api_path = "/wiki-sfb1153/"
            query = "[[Category:Device]]|?HasManufacturer|?HasImage|?HasType"
            return [credential_path, smw_base_url, api_host, query, sfb, api_path, "https"]

        credential_path = '/etc/ckan/default/credentials/smw1368.txt'
        smw_base_url = "https://smw.service.tib.eu/sfb1368/"
        api_host = "smw.service.tib.eu"
        api_path = "/wiki-sfb1368/"
        query = "[[Category:Equipment]]|?hasManufacturer|?hasModel|?depiction"
        return [credential_path, smw_base_url, api_host, query, sfb, api_path, "https"]
