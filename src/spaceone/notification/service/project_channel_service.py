import logging
from jsonschema import validate

from spaceone.core import utils
from spaceone.core.service import *
from spaceone.notification.error import *
from spaceone.notification.lib.schedule import *
from spaceone.notification.lib.schema import *
from spaceone.notification.manager import IdentityManager
from spaceone.notification.manager import ProtocolManager
from spaceone.notification.manager import ProjectChannelManager
from spaceone.notification.manager import SecretManager
from spaceone.notification.model import ProjectChannel

_LOGGER = logging.getLogger(__name__)


@authentication_handler
@authorization_handler
@mutation_handler
@event_handler
class ProjectChannelService(BaseService):
    resource = "ProjectChannel"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.project_channel_mgr: ProjectChannelManager = self.locator.get_manager(
            "ProjectChannelManager"
        )
        self.identity_mgr: IdentityManager = self.locator.get_manager("IdentityManager")
        self.protocol_mgr: ProtocolManager = self.locator.get_manager("ProtocolManager")
        self.secret_mgr: SecretManager = self.locator.get_manager("SecretManager")

    @transaction(
        permission="notification:ProjectChannel.write",
        role_types=["WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @check_required(
        ["protocol_id", "name", "data", "project_id", "workspace_id", "domain_id"]
    )
    def create(self, params):
        """Create Project Channel
        Args:
            params (dict): {
                'protocol_id': 'str',           # required
                'name': 'str',                  # required
                'data': 'dict',                 # required
                'is_subscribe': 'bool',
                'subscriptions': 'list',
                'notification_level': 'str',
                'is_scheduled': 'bool',
                'schedule': 'dict',
                'project_id': 'str',
                'tags': 'dict',
                'workspace_id': 'str'           # injected from auth
                'domain_id': 'str'              # injected from auth
            }

        Returns:
            project_channel_vo (object)
        """

        protocol_id = params["protocol_id"]
        domain_id = params["domain_id"]
        workspace_id = params["workspace_id"]
        data = params["data"]
        project_id = params["project_id"]
        is_subscribe = params.get("is_subscribe", False)
        is_scheduled = params.get("is_scheduled", False)

        if not is_subscribe:
            params["subscriptions"] = []

        if is_scheduled:
            validate_schedule(params.get("schedule", {}))
        else:
            params["schedule"] = None

        self.identity_mgr.get_resource(project_id, "identity.Project", domain_id)
        protocol_vo = self.protocol_mgr.get_protocol(protocol_id, domain_id)

        if protocol_vo.state == "DISABLED":
            raise ERROR_PROTOCOL_DISABLED()

        metadata = protocol_vo.plugin_info.metadata
        schema = metadata.get("data", {}).get("schema")  # TODO: change to schema_id

        if schema:
            validate_json_schema(data, schema)

        if metadata["data_type"] == "SECRET":
            new_secret_parameters = {
                "name": utils.generate_id("project-ch", 4),
                "data": data,
                "resource_group": "WORKSPACE",
                "project_id": project_id,
                "workspace_id": workspace_id,
            }

            project_channel_secret = self.secret_mgr.create_secret(
                new_secret_parameters
            )

            params.update(
                {"secret_id": project_channel_secret["secret_id"], "data": {}}
            )

        # Create Project Channel
        return self.project_channel_mgr.create_project_channel(params)

    @transaction(
        permission="notification:ProjectChannel.write",
        role_types=["WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @check_required(["project_channel_id", "workspace_id", "domain_id"])
    def update(self, params: dict):
        """Update project channel

        Args:
            params (dict): {
                'project_channel_id': 'str',
                'name': 'str',
                'data': 'dict',
                'notification_level': 'str',
                'tags': 'dict',
                'workspace_id': 'str',
                'domain_id': 'str'
            }

        Returns:
            project_channel_vo (object)
        """
        project_channel_id = params["project_channel_id"]
        workspace_id = params["workspace_id"]
        domain_id = params["domain_id"]

        project_channel_vo: ProjectChannel = (
            self.project_channel_mgr.get_project_channel(
                project_channel_id, workspace_id, domain_id
            )
        )

        if "data" in params:
            protocol_vo = self.protocol_mgr.get_protocol(
                project_channel_vo.protocol_id, domain_id
            )
            metadata = protocol_vo.plugin_info.metadata
            schema = metadata.get("data", {}).get("schema")  # TODO: change to schema_id

            if schema:
                validate_json_schema(params["data"], schema)

            if project_channel_vo.secret_id:
                secret_params = {
                    "secret_id": project_channel_vo.secret_id,
                    "data": params["data"],
                    "domain_id": domain_id,
                }

                self.secret_mgr.update_secret_data(secret_params)
                params["data"] = {}

        return self.project_channel_mgr.update_project_channel_by_vo(
            params, project_channel_vo
        )

    @transaction(
        permission="notification:ProjectChannel.write",
        role_types=["WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @check_required(["project_channel_id", "workspace_id", "domain_id"])
    def set_schedule(self, params: dict):
        """Set schedule for Project Channel

        Args:
            params (dict): {
                'project_channel_id': 'str',
                'is_scheduled': bool,
                'schedule': dict,
                'workspace_id': 'str',          # injected from auth
                'domain_id': 'str'              # injected from auth
            }

        Returns:
            project_channel_vo (object)
        """

        project_channel_vo = self.project_channel_mgr.get_project_channel(
            params["project_channel_id"], params["workspace_id"], params["domain_id"]
        )

        is_scheduled = params.get("is_scheduled", False)

        if is_scheduled:
            validate_schedule(params.get("schedule", {}))
        else:
            params.update({"is_scheduled": False, "schedule": None})

        return self.project_channel_mgr.update_project_channel_by_vo(
            params, project_channel_vo
        )

    @transaction(
        permission="notification:ProjectChannel.write",
        role_types=["WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @check_required(["project_channel_id", "workspace_id", "domain_id"])
    def set_subscription(self, params):
        """Set subscriptions for Project Channel

        Args:
            params (dict): {
                'project_channel_id': 'str',    # required
                'is_subscribe': bool,
                'subscriptions': list,
                'workspace_id': 'str',          # injected from auth
                'domain_id': 'str'              # injected from auth
            }

        Returns:
            project_channel_vo (object)
        """
        if not params.get("is_subscribe", False):
            params.update({"is_subscribe": False, "subscriptions": []})

        proejct_channel_vo = self.project_channel_mgr.get_project_channel(
            params["project_channel_id"], params["workspace_id"], params["domain_id"]
        )
        proejct_channel_vo = self.project_channel_mgr.update_project_channel_by_vo(
            params, proejct_channel_vo
        )
        return proejct_channel_vo

    @transaction(
        permission="notification:ProjectChannel.write",
        role_types=["WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @check_required(["project_channel_id", "workspace_id", "domain_id"])
    def delete(self, params):
        """Delete project channel

        Args:
            params (dict): {
                'project_channel_id': 'str',
                'workspace_id': 'str',          # injected from auth
                'domain_id': 'str'              # injected from auth
            }

        Returns:
            None
        """
        project_channel_id = params["project_channel_id"]
        workspace_id = params["workspace_id"]
        domain_id = params["domain_id"]

        project_channel_vo = self.project_channel_mgr.get_project_channel(
            project_channel_id, workspace_id, domain_id
        )

        if secret_id := project_channel_vo.secret_id:
            self.secret_mgr.delete_secret(secret_id)

        self.project_channel_mgr.delete_project_channel_by_vo(project_channel_vo)

    @transaction(
        permission="notification:ProjectChannel.write",
        role_types=["WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @check_required(["project_channel_id", "workspace_id", "domain_id"])
    def enable(self, params):
        """Enable project channel

        Args:
            params (dict): {
                'project_channel_id': 'str',    # required
                'workspace_id': 'str',          # injected from auth
                'domain_id': 'str'              # injected from auth
            }

        Returns:
            project_channel_vo (object)
        """

        project_channel_vo = self.project_channel_mgr.get_project_channel(
            params["project_channel_id"], params["workspace_id"], params["domain_id"]
        )

        project_channel_vo = self.project_channel_mgr.enable_project_channel(
            project_channel_vo
        )

        return project_channel_vo

    @transaction(
        permission="notification:ProjectChannel.write",
        role_types=["WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @check_required(["project_channel_id", "workspace_id", "domain_id"])
    def disable(self, params):
        """Disable project channel

        Args:
            params (dict): {
                'project_channel_id': 'str',    # required
                'workspace_id': 'str',          # injected from auth
                'domain_id': 'str'              # injected from auth
            }

        Returns:
            project_channel_vo (object)
        """

        project_channel_vo = self.project_channel_mgr.get_project_channel(
            params["project_channel_id"], params["workspace_id"], params["domain_id"]
        )

        project_channel_vo = self.project_channel_mgr.disable_project_channel(
            project_channel_vo
        )

        return project_channel_vo

    @transaction(
        permission="notification:ProjectChannel.read",
        role_types=["DOMAIN_OWNER", "WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @check_required(["project_channel_id", "workspace_id", "domain_id"])
    def get(self, params):
        """Get Project Channel

        Args:
            params (dict): {
                'project_channel_id': 'str',    # required
                'workspace_id': 'str',          # injected from auth
                'domain_id': 'str',             # injected from auth
            }

        Returns:
            project_channel_vo (object)
        """
        project_channel_vo = self.project_channel_mgr.get_project_channel(
            params["project_channel_id"], params["workspace_id"], params["domain_id"]
        )
        return project_channel_vo

    @transaction(
        permission="notification:ProjectChannel.read",
        role_types=["DOMAIN_OWNER", "WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @check_required(["domain_id"])
    @append_query_filter(
        [
            "project_channel_id",
            "name",
            "state",
            "secret_id",
            "is_subscribe",
            "is_scheduled",
            "notification_level",
            "protocol_id",
            "project_id",
            "workspace_id",
            "domain_id",
            "user_projects",
        ]
    )
    @append_keyword_filter(["project_channel_id", "name"])
    def list(self, params):
        """List Project Channels
                Args:
            params (dict): {
                'query': 'dict (spaceone.api.core.v1.Query)',
                'project_channel_id': 'str',
                'name': 'str',
                'state': 'str',
                'secret_id': 'str',
                'is_subscribe': 'bool',
                'is_scheduled': 'bool',
                'notification_level': 'str',
                'protocol_id': 'str',
                'project_id': 'str',
                'workspace_id': 'str',
                'domain_id': 'str',
                'user_projects': 'list', // from meta
            }

        Returns:
            results (list): 'list of project_channel_vo'
            total_count (int)
        """
        query = params.get("query", {})
        return self.project_channel_mgr.list_project_channels(query)

    @transaction(
        permission="notification:ProjectChannel.read",
        role_types=["DOMAIN_OWNER", "WORKSPACE_OWNER", "WORKSPACE_MEMBER"],
    )
    @check_required(["query", "domain_id"])
    @append_query_filter(["domain_id", "user_projects"])
    @append_keyword_filter(["project_channel_id", "name"])
    def stat(self, params):
        """
        Args:
            params (dict): {
                'query': 'dict (spaceone.api.core.v1.StatisticsQuery)',
                'domain_id': 'str',
                'user_projects': 'list', // from meta
            }

        Returns:
            values (list): 'list of statistics data'
            total_count (int)
        """
        query = params.get("query", {})
        return self.project_channel_mgr.stat_project_channels(query)
