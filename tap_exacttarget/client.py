import FuelSDK
import singer


LOGGER = singer.get_logger()


def _get_response_items(response):
    items = response.results

    if 'count' in response.results:
        LOGGER.info('Got {} results.'.format(response.results.get('count')))
        items = response.results.get('items')

    return items


__all__ = ['get_auth_stub', 'request', 'request_from_cursor']


# PUBLIC FUNCTIONS

def get_auth_stub(config):
    """
    Given a config dict in the format:

        {'clientid': ... your ET client ID ...,
         'clientsecret': ... your ET client secret ...}

    ... return an auth stub to be used when making requests.
    """
    LOGGER.info("Generating auth stub...")

    auth_stub = FuelSDK.ET_Client(
        params={
            'clientid': config['client_id'],
            'clientsecret': config['client_secret']
        })

    LOGGER.info("Success.")

    return auth_stub


def request(name, selector, auth_stub, search_filter=None, props=None):
    """
    Given an object name (`name`), used for logging purposes only,
      a `selector`, for example FuelSDK.ET_ClickEvent,
      an `auth_stub`, generated by `get_auth_stub`,
      an optional `search_filter`,
      and an optional set of `props` (properties), which specifies the fields
        to be returned from this object,

    ... request data from the ExactTarget API using FuelSDK. This function
    returns a generator that will yield all the records returned by the
    request.

    Example `search_filter`:

        {'Property': 'CustomerKey',
         'SimpleOperator': 'equals',
         'Value': 'abcdef'}

    For more on search filters, see:
      https://developer.salesforce.com/docs/atlas.en-us.noversion.mc-apis.meta/mc-apis/using_complex_filter_parts.htm
    """
    cursor = selector()
    cursor.auth_stub = auth_stub

    if props is not None:
        cursor.props = props

    if search_filter is not None:
        cursor.search_filter = search_filter

        LOGGER.info(
            "Making RETRIEVE call to '{}' endpoint with filters '{}'."
            .format(name, search_filter))

    else:
        LOGGER.info(
            "Making RETRIEVE call to '{}' endpoint with no filters."
            .format(name))

    return request_from_cursor(name, cursor)


def request_from_cursor(name, cursor):
    """
    Given an object name (`name`), used for logging purposes only, and a
    `cursor` provided by FuelSDK, return a generator that yields all the
    items in that cursor.

    Primarily used internally by `request`, but can be used if cursors have
    to be customized. See tap_exacttarget.endpoints.data_extensions for
    an example.
    """
    response = cursor.get()

    if not response.status:
        LOGGER.warn("Request failed with '{}'"
                    .format(response.message))

    for item in _get_response_items(response):
        yield item

    while response.more_results:
        LOGGER.info("Getting more results from '{}' endpoint".format(name))

        response = response.getMoreResults()

        if not response.status:
            LOGGER.warn("Request failed with '{}'"
                        .format(response.message))

        LOGGER.info('Got {} results.'.format(response.results.get('count')))

        for item in _get_response_items(response):
            yield item

    LOGGER.info("Done retrieving results from '{}' endpoint".format(name))
