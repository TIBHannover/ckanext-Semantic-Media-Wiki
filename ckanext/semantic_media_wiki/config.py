import logging


log = logging.getLogger(__name__)

MEDIAWIKI_CREDENTIALS_PATH = "ckanext.mediawiki_credentials_path"
SMW_BASE_URL = "ckanext.smw.baseurl"
MEDIAWIKI_API_ENDPOINT = "ckanext.smw.mediawiki.api.endpoint"
MEDIAWIKI_API_PATH = "ckanext.smw.mediawiki.api.path"
MEDIAWIKI_API_SCHEME = "ckanext.smw.mediawiki.api.scheme"

LEGACY_MEDIAWIKI_API_ENDPONT = "ckanext.smw.mediaWiki.api.endpont"


def apply_historical_endpoint_config(config):
    """Support the endpoint typo that CKAN cannot declare as a second alias."""
    if config.get(MEDIAWIKI_API_ENDPOINT) is not None:
        return
    if LEGACY_MEDIAWIKI_API_ENDPONT not in config:
        return

    log.warning(
        "Config option '%s' is deprecated. Use '%s' instead",
        LEGACY_MEDIAWIKI_API_ENDPONT,
        MEDIAWIKI_API_ENDPOINT,
    )
    config[MEDIAWIKI_API_ENDPOINT] = config[LEGACY_MEDIAWIKI_API_ENDPONT]
