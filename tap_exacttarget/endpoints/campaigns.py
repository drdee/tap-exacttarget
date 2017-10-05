import FuelSDK
import singer

from tap_exacttarget.client import request
from tap_exacttarget.dao import DataAccessObject


LOGGER = singer.get_logger()


class CampaignDataAccessObject(DataAccessObject):

    SCHEMA = {
        'type': 'object',
        'properties': {
            'id': {
                'type': 'string',
            },
            'createdDate': {
                'type': 'string',
            },
            'modifiedDate': {
                'type': 'string',
            },
            'name': {
                'type': 'string',
            },
            'description': {
                'type': 'string',
            },
            'campaignCode': {
                'type': 'string',
            },
            'color': {
                'type': 'string',
            }
        }
    }

    TABLE = 'campaign'
    KEY_PROPERTIES = ['id']

    def parse_object(self, obj):
        to_return = obj.copy()


        return obj

    def sync_data(self):
        cursor = request(
            'Campaign',
            FuelSDK.ET_Campaign,
            self.auth_stub)

        for campaign in cursor:
            campaign = self.filter_keys_and_parse(campaign)

            singer.write_records(self.__class__.TABLE, [campaign])
