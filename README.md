# ckanext-Semantic-Media-Wiki

This CKAN extension includes `semantic_media_wiki` plugin that aim to able users to link machines on semantic media wiki to resources/datasets in CKAN.



## Requirements

Compatibility with core CKAN versions:

| CKAN version    | Compatible?   |
| --------------- | ------------- |
|  2.9 | Yes    |
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

3. Add `semantic_media_wiki` and `sample_link` to the `ckan.plugins` setting in your CKAN
   config file (by default the config file is located at
   `/etc/ckan/default/ckan.ini`).

4. Upgrade the CKAN database to add the plugin table:

        ckan -c /etc/ckan/default/ckan.ini db upgrade -p semantic_media_wiki

        ckan -c /etc/ckan/default/ckan.ini db upgrade -p sample_link


4. Restart CKAN and supervisor. For example if you've deployed CKAN with nginx on Ubuntu:

        sudo service supervisor reload
        sudo service nginx reload
        


## config
These plugins need the following variables provided in `ckan.ini`


        ckanext.crc.project.id="CRC_Project_ID"
        
        ckanext.smw.equipment.endpoint=""
        
        ckanext.smw.machine.endpoint=""
        
        ckanext.smw.tools.endpoint=""



## Tests

To run the tests, do:

    pytest --ckan-ini=test.ini  --disable-pytest-warnings  ckanext/semantic_media_wiki/tests/


