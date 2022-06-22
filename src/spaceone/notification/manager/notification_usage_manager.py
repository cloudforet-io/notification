import logging
from spaceone.core.manager import BaseManager
from spaceone.notification.model.notification_usage_model import NotificationUsage

_LOGGER = logging.getLogger(__name__)


class NotificationUsageManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.noti_usage_model: NotificationUsage = self.locator.get_model('NotificationUsage')

    def create_notification_usage(self, params):
        def _rollback(noti_usage_vo):
            _LOGGER.info(f'[create_notification_usage._rollback]'
                         f'Delete Notification Usage : {noti_usage_vo.protocol_id}'
                         f'({noti_usage_vo.protocol_id})')
            noti_usage_vo.delete()

        noti_usage_vo: NotificationUsage = self.noti_usage_model.create(params)
        self.transaction.add_rollback(_rollback, noti_usage_vo)

        return noti_usage_vo

    def get_notification_usage(self, protocol_id, usage_month, usage_date, domain_id, only=None):
        return self.noti_usage_model.get(protocol_id=protocol_id,
                                         usage_month=usage_month, usage_date=usage_date,
                                         domain_id=domain_id, only=only)

    def list_notification_usages(self, query={}):
        return self.noti_usage_model.query(**query)

    def stat_notification_usages(self, query):
        return self.noti_usage_model.stat(**query)

    @staticmethod
    def incremental_notification_usage(noti_usage_vo, count):
        noti_usage_vo.increment("count", count)

    @staticmethod
    def incremental_notification_fail_count(noti_usage_vo, count):
        noti_usage_vo.increment("fail_count", count)
