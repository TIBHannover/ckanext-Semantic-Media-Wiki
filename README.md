# ckanext-Semantic-Media-Wiki

This CKAN extension includes `semantic_media_wiki` plugin that aim to able users to link machines on semantic media wiki to resources/datasets in CKAN.



## Requirements

Compatibility with core CKAN versions:

| CKAN version    | Compatible?   |
| --------------- | ------------- |
| 2.9 | Yes |
| 2.10 | Yes |
| 2.11 | CI target |
| earlier | No |           |



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

3. Add the required plugin names to the `ckan.plugins` setting in your CKAN
   config file (by default the config file is located at
   `/etc/ckan/default/ckan.ini`).

   SFB1153 uses:

        ckan.plugins = ... machine_link sample_link

   SFB1368 uses:

        ckan.plugins = ... machine_link protocol_link

   The full extension test configuration loads all three plugins together:

        ckan.plugins = ... machine_link sample_link protocol_link

4. Upgrade the CKAN database to add the plugin table:

        ckan -c /etc/ckan/default/ckan.ini db upgrade -p machine_link

        ckan -c /etc/ckan/default/ckan.ini db upgrade -p sample_link

        ckan -c /etc/ckan/default/ckan.ini db upgrade -p protocol_link


4. Restart CKAN and supervisor. For example if you've deployed CKAN with nginx on Ubuntu:

        sudo service supervisor reload
        sudo service nginx reload
        


## config
These plugins need the following variables provided in `ckan.ini`


        ckanext.crc.project.id="CRC_Project_ID"

        ckanext.mediaWiki_credentials_path=""
        
        ckanext.smw.baseUrl=""

        ckanext.smw.mediaWiki.api.endpoint=""

        ckanext.smw.mediaWiki.path="/wiki/"

        ckanext.smw.mediaWiki.scheme="https"

        ckanext.smw.mediaWiki.timeout=30
        
        ckanext.smw.equipment.endpoint=""
        
        ckanext.smw.machine.endpoint=""
        
        ckanext.smw.tools.endpoint=""

The legacy misspelled key `ckanext.smw.mediaWiki.api.endpont` is still read
as a fallback, but new configuration should use
`ckanext.smw.mediaWiki.api.endpoint`.



## Tests

To run the tests, do:

    pytest --ckan-ini=test.ini --disable-warnings ckanext/semantic_media_wiki

The tests mock MediaWiki calls and must not call a real MediaWiki server.

For a later combined docker-ckan integration test with dependent extensions:

* install this extension together with the dependent SFB1153/SFB1368 plugins;
* enable `machine_link sample_link` for SFB1153;
* enable `machine_link protocol_link` for SFB1368;
* provide test-only MediaWiki endpoint/configuration or mocks;
* verify plugin load order and template interactions with the dependent layout
  extensions.

