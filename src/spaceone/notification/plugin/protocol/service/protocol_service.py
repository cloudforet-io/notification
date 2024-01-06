import logging
from typing import Generator, Union
from spaceone.core.service import BaseService, transaction, convert_model
from spaceone.notification.plugin.protocol.model.protocol_request import (
    ProtocolInitRequest,
    ProtocolVerifyRequest,
)
from spaceone.notification.plugin.protocol.model.protocol_response import PluginResponse

_LOGGER = logging.getLogger(__name__)


class ProtocolService(BaseService):
    resource = "Protocol"

    @transaction()
    @convert_model
    def init(self, params: ProtocolInitRequest) -> Union[dict, PluginResponse]:
        """init plugin by options

        Args:
            params (ProtocolInitRequest): {
                'options': 'dict',    # Required
                'domain_id': 'str'
            }

        Returns:
            PluginResponse:
        """

        func = self.get_plugin_method("init")
        response = func(params.dict())
        return PluginResponse(**response)

    @transaction()
    @convert_model
    def verify(self, params: ProtocolVerifyRequest) -> None:
        """Verifying protocol plugin

        Args:
            params (ProtocolVerifyRequest): {
                'options': 'dict',      # Required
                'secret_data': 'dict',  # Required
                'domain_id': 'str'
            }

        Returns:
            None
        """

        func = self.get_plugin_method("verify")
        func(params.dict())
