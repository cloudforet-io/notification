import logging
from spaceone.core.service import BaseService, transaction, convert_model
from spaceone.notification.plugin.protocol.model.notification_request import (
    NotificationDispatchRequest,
)

_LOGGER = logging.getLogger(__name__)


class NotificationService(BaseService):
    resource = "Notification"

    @transaction()
    @convert_model
    def dispatch(self, params: NotificationDispatchRequest) -> None:
        """dispatch notification

        Args:
            params (NotificationDispatchRequest): {
                'options': 'dict',                  # Required
                'secret_data': 'dict',              # Required
                'channel_data': 'dict',             # Required
                'message': 'dict',                  # Required
                'notification_type': 'str',         # Required
            }

        Returns:
            None
        """

        func = self.get_plugin_method("dispatch")
        func(params.dict())
