import logging
from spaceone.core.manager import BaseManager
from spaceone.notification.model.notification_model import Notification
from pprint import pprint
from spaceone.notification.error import *

_LOGGER = logging.getLogger(__name__)


class NotificationManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.notification_model: Notification = self.locator.get_model('Notification')

    def create_notification(self, params):
        def _rollback(notification_vo):
            _LOGGER.info(f'[create_protocol._rollback]'
                         f'Delete Notification : {notification_vo.name}'
                         f'({notification_vo.protocol_id})')
            notification_vo.delete()
        pprint(params)
        notification_vo: Notification = self.notification_model.create(params)
        self.transaction.add_rollback(_rollback, notification_vo)

        return notification_vo

    def delete_notification(self, protocol_id, domain_id):
        notification_vo: Notification = self.get_protocol(protocol_id, domain_id)
        # TODO: Required to check existed channel using protocol
        notification_vo.delete()

    def get_notification(self, protocol_id, domain_id, only=None):
        return self.notification_model.get(protocol_id=protocol_id, domain_id=domain_id, only=only)

    def list_notifications(self, query={}):
        return self.notification_model.query(**query)

    def stat_notifications(self, query):
        return self.notification_model.stat(**query)
