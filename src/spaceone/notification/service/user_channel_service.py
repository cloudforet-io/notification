import logging

from spaceone.core import utils
from spaceone.core.service import *

from spaceone.notification.error import *
from spaceone.notification.lib.schedule import *
from spaceone.notification.lib.schema import *
from spaceone.notification.manager import IdentityManager
from spaceone.notification.manager import UserChannelManager
from spaceone.notification.manager import UserSecretManager
from spaceone.notification.model import UserChannel
from spaceone.notification.manager import ProtocolManager
from spaceone.notification.model.protocol_model import Protocol

_LOGGER = logging.getLogger(__name__)


@authentication_handler
@authorization_handler
@mutation_handler
@event_handler
class UserChannelService(BaseService):
    resource = "UserChannel"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_channel_mgr: UserChannelManager = self.locator.get_manager(
            "UserChannelManager"
        )
        self.identity_mgr: IdentityManager = self.locator.get_manager("IdentityManager")
        self.protocol_mgr: ProtocolManager = self.locator.get_manager("ProtocolManager")
        self.user_secret_mgr: UserSecretManager = self.locator.get_manager(
            "UserSecretManager"
        )

    @transaction(
        permission="notification:UserChannel.write",
        role_types=["USER"],
    )
    @check_required(["protocol_id", "name", "data", "user_id", "domain_id"])
    def create(self, params):
        """Create user Channel

        Args:
            params (dict): {
                'protocol_id': 'str',       # required
                'name': 'str',              # required
                'data': 'dict',             # required
                'is_subscribe': 'bool',
                'subscriptions': 'list',
                'is_scheduled': 'bool',
                'schedule': 'dict',
                'tags': 'dict',
                'user_id': 'str',           # injected from auth
                'domain_id': 'str'          # injected from auth
            }

        Returns:
            user_channel_vo (object)
        """

        protocol_id = params["protocol_id"]
        domain_id = params["domain_id"]
        data = params["data"]
        user_id = params["user_id"]
        is_subscribe = params.get("is_subscribe", False)
        is_scheduled = params.get("is_scheduled", False)

        if not is_subscribe:
            params["subscriptions"] = []

        if is_scheduled:
            validate_schedule(params.get("schedule", {}))
        else:
            params["schedule"] = None

        self.identity_mgr.get_user_profile()
        protocol_vo: Protocol = self.protocol_mgr.get_protocol(protocol_id, domain_id)

        if protocol_vo.state == "DISABLED":
            raise ERROR_PROTOCOL_DISABLED()

        if protocol_vo.protocol_type == "INTERNAL":
            raise ERROR_PROTOCOL_INTERNVAL()

        metadata = protocol_vo.plugin_info.metadata
        schema = metadata.get("data", {}).get("schema", {})
        if schema:
            validate_json_schema(schema, data)

        if metadata["data_type"] == "SECRET":
            new_secret_parameters = {
                "name": utils.generate_id("user-ch", 4),
                "data": data,
            }

            user_channel_secret = self.user_secret_mgr.create_user_secret(
                new_secret_parameters
            )

            params.update(
                {"user_secret_id": user_channel_secret["user_secret_id"], "data": {}}
            )

        return self.user_channel_mgr.create_user_channel(params)

    @transaction(
        permission="notification:UserChannel.write",
        role_types=["USER"],
    )
    @check_required(["user_channel_id", "user_id", "domain_id"])
    def update(self, params):
        """Update user channel

        Args:
            params (dict): {
                'user_channel_id': 'str',       # required
                'name': 'str',
                'data': 'dict',
                'tags': 'dict',
                'user_id' 'str',                # injected from auth
                'domain_id': 'str'              # injected from auth
            }

        Returns:
            user_channel_vo (object)
        """

        user_channel_id = params["user_channel_id"]
        domain_id = params["domain_id"]
        user_id = params["user_id"]

        user_channel_vo: UserChannel = self.user_channel_mgr.get_user_channel(
            user_channel_id, user_id, domain_id
        )

        if "data" in params and user_channel_vo.user_secret_id:
            secret_params = {
                "user_secret_id": user_channel_vo.user_secret_id,
                "data": params["data"],
            }

            self.user_secret_mgr.update_user_secret_data(secret_params)
            params["data"] = {}

        return self.user_channel_mgr.update_user_channel_by_vo(params, user_channel_vo)

    @transaction(
        permission="notification:UserChannel.write",
        role_types=["USER"],
    )
    @check_required(["user_channel_id", "user_id", "domain_id"])
    def set_schedule(self, params):
        """
            set_schedule
        Args:
            params (dict): {
                'user_channel_id': 'str',       # required
                'is_scheduled': bool,
                'schedule': dict,
                'user_id' 'str',                # injected from auth
                'domain_id': 'str'              # injected from auth
            }

        Returns:
            user_channel_vo (object)
        """

        user_channel_vo = self.user_channel_mgr.get_user_channel(
            params["user_channel_id"], params["user_id"], params["domain_id"]
        )

        is_scheduled = params.get("is_scheduled", False)

        if is_scheduled:
            validate_schedule(params.get("schedule", {}))
        else:
            params.update({"is_scheduled": False, "schedule": None})

        return self.user_channel_mgr.update_user_channel_by_vo(params, user_channel_vo)

    @transaction(
        permission="notification:UserChannel.write",
        role_types=["USER"],
    )
    @check_required(["user_channel_id", "user_id", "domain_id"])
    def set_subscription(self, params):
        """
            set_subscription
        Args:
            params (dict): {
                'user_channel_id': 'str',
                'is_subscribe': bool,
                'subscriptions': list,
                'domain_id': 'str'
            }

        Returns:
            user_channel_vo (object)
        """
        if not params.get("is_subscribe", False):
            params.update({"is_subscribe": False, "subscriptions": []})

        user_channel_vo = self.get_user_channel(
            params["user_channel_id"], params["user_id"], params["domain_id"]
        )
        return self.user_channel_mgr.update_user_channel_by_vo(params, user_channel_vo)

    @transaction(
        permission="notification:UserChannel.write",
        role_types=["USER"],
    )
    @check_required(["user_channel_id", "user_id", "domain_id"])
    def delete(self, params):
        """Delete user channel

        Args:
            params (dict): {
                'user_channel_id': 'str',
                "user_id": "str",
                'domain_id': 'str'
            }

        Returns:
            None
        """
        user_channel_id = params["user_channel_id"]
        user_id = params["user_id"]
        domain_id = params["domain_id"]

        user_channel_vo = self.user_channel_mgr.get_user_channel(
            user_channel_id, user_id, domain_id
        )

        if user_secret_id := user_channel_vo.user_secret_id:
            self.user_secret_mgr.delete_user_secret(user_secret_id)

        self.user_channel_mgr.delete_user_channel_by_vo(user_channel_vo)

    @transaction(
        permission="notification:UserChannel.write",
        role_types=["USER"],
    )
    @check_required(["user_channel_id", "domain_id"])
    def enable(self, params):
        """Enable user channel

        Args:
            params (dict): {
                'user_channel_id': 'str',
                'domain_id': 'str'
            }

        Returns:
            user_channel_vo (object)
        """
        user_channel_vo = self.user_channel_mgr.get_user_channel(
            params["user_channel_id"], params["user_id"], params["domain_id"]
        )
        user_channel_vo = self.user_channel_mgr.enable_user_channel(user_channel_vo)
        return user_channel_vo

    @transaction(
        permission="notification:UserChannel.write",
        role_types=["USER"],
    )
    @check_required(["user_channel_id", "user_id", "domain_id"])
    def disable(self, params):
        """Disable user channel

        Args:
            params (dict): {
                'user_channel_id': 'str',   # required
                'user_id': 'str',           # injected from auth
                'domain_id': 'str'          # injected from auth
            }

        Returns:
            user_channel_vo (object)
        """
        user_channel_vo = self.user_channel_mgr.get_user_channel(
            params["user_channel_id"], params["user_id"], params["domain_id"]
        )
        user_channel_vo = self.user_channel_mgr.disable_user_channel(user_channel_vo)
        return user_channel_vo

    @transaction(
        permission="notification:UserChannel.read",
        role_types=["USER"],
    )
    @check_required(["user_channel_id", "user_id", "domain_id"])
    def get(self, params):
        """Get User Channel

        Args:
            params (dict): {
                'user_channel_id': 'str',   # required
                'user_id': 'str',           # injected from auth
                'domain_id': 'str',         # injected from auth
            }

        Returns:
            user_channel_vo (object)
        """

        return self.user_channel_mgr.get_user_channel(
            params["user_channel_id"], params["user_id"], params["domain_id"]
        )

    @transaction(
        permission="notification:UserChannel.read",
        role_types=["USER"],
    )
    @check_required(["user_id", "domain_id"])
    @append_query_filter(
        [
            "user_channel_id",
            "name",
            "state",
            "user_secret_id",
            "protocol_id",
            "user_id",
            "domain_id",
        ]
    )
    @append_keyword_filter(["user_channel_id", "name"])
    def list(self, params):
        """List User Channels

        Args:
            params (dict): {
                'query': 'dict (spaceone.api.core.v1.Query)'
                'user_channel_id': 'str',
                'name': 'str',
                'state': 'str',
                'user_secret_id': 'str',
                'protocol_id': 'str',
                'user_id': 'str',                               # injected from auth
                'domain_id': 'str',                             # injected from auth
            }

        Returns:
            results (list): 'list of user_channel_vo'
            total_count (int)
        """

        query = params.get("query", {})
        return self.user_channel_mgr.list_user_channels(query)

    @transaction(
        permission="notification:UserChannel.read",
        role_types=["USER"],
    )
    @check_required(["query", "domain_id"])
    @append_query_filter(["domain_id", "user_self"])
    @append_keyword_filter(["user_channel_id", "name"])
    def stat(self, params):
        """
        Args:
            params (dict): {
                'domain_id': 'str',
                'query': 'dict (spaceone.api.core.v1.StatisticsQuery)'
            }

        Returns:
            values (list): 'list of statistics data'
            total_count (int)
        """

        query = params.get("query", {})
        return self.user_channel_mgr.stat_user_channels(query)
