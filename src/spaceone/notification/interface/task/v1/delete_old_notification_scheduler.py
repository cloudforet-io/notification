import logging

from spaceone.core import config
from spaceone.core.locator import Locator
from spaceone.core.scheduler import IntervalScheduler

_LOGGER = logging.getLogger(__name__)


class DeleteOldNotificationScheduler(IntervalScheduler):

    def __init__(self, queue, interval):
        super().__init__(queue, interval)
        self.locator = Locator()
        self._init_config()
        self._create_metadata()

    def _init_config(self):
        self._token = config.get_global('TOKEN')

    def _create_metadata(self):
        self._metadata = {
            'token': self._token,
            'service': 'notification',
            'resource': 'Notification',
            'verb': 'delete_old_notifications'
        }

    def create_task(self):
        task = {
            'name': 'delete_old_notification_scheduler',
            'version': 'v1',
            'executionEngine': 'BaseWorker',
            'stages': [{
                'locator': 'SERVICE',
                'name': 'NotificationService',
                'metadata': self._metadata,
                'method': 'delete_old_notifications',
                'params': {
                    'params': {}
                }
            }]
        }

        return [task]
