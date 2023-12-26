import logging
from spaceone.core.manager import BaseManager
from spaceone.notification.model.notification_model import Notification
from spaceone.notification.error import *

_LOGGER = logging.getLogger(__name__)


class NotificationManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.notification_model: Notification = self.locator.get_model("Notification")

    def create_notification(self, params):
        def _rollback(vo: Notification):
            _LOGGER.info(
                f"[create_protocol._rollback]"
                f"Delete Notification : {vo.notification_id}"
                f"({notification_vo.user_id})"
                f"({notification_vo.domain_id})"
            )
            notification_vo.delete()

        notification_vo: Notification = self.notification_model.create(params)
        self.transaction.add_rollback(_rollback, notification_vo)

        return notification_vo

    def set_read_notification(self, notifications, domain_id):
        def _rollback(notification_vos):
            _LOGGER.info(f"[set_read_notification._rollback]")
            notification_vos.update({"is_read": False})

        query = {
            "filter": [
                {"k": "notification_id", "v": notifications, "o": "in"},
                {"k": "domain_id", "v": domain_id, "o": "eq"},
                {"k": "is_read", "v": False, "o": "eq"},
            ]
        }

        notification_vos, total_count = self.list_notifications(query)
        self.transaction.add_rollback(_rollback, notification_vos)
        notification_vos.update({"is_read": True})

    def get_notification(self, notification_id: str, domain_id: str):
        return self.notification_model.get(
            notification_id=notification_id, domain_id=domain_id
        )

    def list_notifications(self, query):
        return self.notification_model.query(**query)

    def stat_notifications(self, query):
        return self.notification_model.stat(**query)

    def filter_notifications(self, **conditions):
        return self.notification_model.filter(**conditions)

    @staticmethod
    def delete_notification_by_vos(notification_vos):
        notification_vos.delete()
