import logging
from typing import Generator, Union
from spaceone.core.service import BaseService, transaction, convert_model
from spaceone.notification.plugin.protocol.model.notification_request import NotificationDispatchRequest
from spaceone.notification.plugin.protocol.model.notification_response import ResourceResponse

_LOGGER = logging.getLogger(__name__)


class NotificationService(BaseService):
    @transaction
    @convert_model
    def dispatch(self, params: NotificationDispatchRequest) -> Union[Generator[ResourceResponse, None, None], dict]:
        """ dispatch notification

        Args:
            params (NotificationDispatchRequest): {
                'options': 'dict',      # Required
                'secret_data': 'dict',  # Required
                'channel_data': 'dict', # Required
                'message': 'dict',
                'notification_type': 'str',
            }

        Returns:
            Generator[ResourceResponse, None, None]
        """

        func = self.get_plugin_method('dispatch')
        response_iterator = func(params.dict())
        for response in response_iterator:
            yield ResourceResponse(**response)