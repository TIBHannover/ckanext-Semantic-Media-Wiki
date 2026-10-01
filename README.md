# ckanext-Semantic-Media-Wiki

This CKAN extension provides `machine_link`, `sample_link`, and `protocol_link`
plugins for linking Semantic MediaWiki entities to CKAN datasets and resources.



## Requirements

Compatibility with core CKAN versions:

| CKAN version | Python | Compatible? |
| ------------ | ------ | ----------- |
| 2.10 | 3.8-3.11 | Yes |
| 2.11 | 3.10-3.12 | Yes |



## Installation

To install ckanext-Semantic-Media-Wiki:

1. Activate your CKAN virtual environment, for example:

        source /usr/lib/ckan/default/bin/activate

2. Clone the source and install it on the virtualenv (Suggested location: /usr/lib/ckan/default/src)
:

        git clone https://github.com/TIBHannover/ckanext-Semantic-Media-Wiki.git
        cd ckanext-Semantic-Media-Wiki
        pip install -e .
        pip install -r requirements.txt

3. Add `machine_link`, `sample_link`, and `protocol_link` to the `ckan.plugins` setting in your CKAN
   config file (by default the config file is located at
   `/etc/ckan/default/ckan.ini`).

4. Upgrade the CKAN database to add each plugin's table:

        ckan -c /etc/ckan/default/ckan.ini db upgrade -p machine_link

        ckan -c /etc/ckan/default/ckan.ini db upgrade -p sample_link

        ckan -c /etc/ckan/default/ckan.ini db upgrade -p protocol_link


5. Restart CKAN and supervisor. For example if you've deployed CKAN with nginx on Ubuntu:

        sudo service supervisor reload
        sudo service nginx reload
        


## config
These plugins need the following variables provided in `ckan.ini`


        ckanext.crc.project.id="CRC_Project_ID"

        ckanext.mediaWiki_credentials_path=""
        
        ckanext.smw.baseUrl=""

        # Legacy misspelled key; the value must contain only the hostname.
        ckanext.smw.mediaWiki.api.endpont="service.tib.eu"

        # Optional. Defaults: /wiki-sfb1153/ for project 1153 and
        # /sfb1368/wiki/ for project 1368.
        ckanext.smw.mediaWiki.api.path="/sfb1368/wiki/"

        ckanext.smw.mediaWiki.api.scheme="https"
        
        ckanext.smw.equipment.endpoint=""
        
        ckanext.smw.machine.endpoint=""
        
        ckanext.smw.tools.endpoint=""

For an SFB1368 deployment using environment variables, configure:

        CKANEXT__CRC__PROJECT__ID=1368
        CKANEXT__SMW__MEDIAWIKI__API__ENDPONT=service.tib.eu
        CKANEXT__SMW__MEDIAWIKI__API__PATH=/sfb1368/wiki/
        CKANEXT__SMW__MEDIAWIKI__API__SCHEME=https

`CKANEXT__SMW__MEDIAWIKI__API__ENDPONT` retains the historical spelling for
backward compatibility and must contain only the hostname, without a scheme or
path.



## Tests

To run the tests, do:

    pytest --ckan-ini=test.ini --disable-warnings ckanext/semantic_media_wiki/tests/

The test suite uses mocked Semantic MediaWiki responses and does not require production credentials or network access.
