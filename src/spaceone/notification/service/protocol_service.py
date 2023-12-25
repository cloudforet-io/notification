import logging
import copy
from typing import Tuple

from spaceone.core import cache
from spaceone.core import utils
from spaceone.core import config
from spaceone.core.service import *

from spaceone.notification.conf.protocol_conf import *
from spaceone.notification.error import *
from spaceone.notification.manager import RepositoryManager
from spaceone.notification.manager import ProtocolManager
from spaceone.notification.manager import PluginManager
from spaceone.notification.manager import ProjectChannelManager
from spaceone.notification.manager import UserChannelManager
from spaceone.notification.manager import SecretManager
from spaceone.notification.model import Protocol

_LOGGER = logging.getLogger(__name__)


@authentication_handler
@authorization_handler
@mutation_handler
@event_handler
class ProtocolService(BaseService):
    resource = "Protocol"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.protocol_mgr: ProtocolManager = self.locator.get_manager("ProtocolManager")

    @transaction(permission="notification:Protocol.write", role_types=["DOMAIN_ADMIN"])
    @check_required(["name", "plugin_info", "domain_id"])
    def create(self, params):
        """Create Protocol
        Args:
            params (dict): {
                'name': 'str',          # required
                'plugin_info': 'dict',  # required
                'tags': 'dict',
                'domain_id': 'str',     # injected from auth
            }

        Returns:
            protocol_vo (object)
        """
        return self._create(params)

    def _create(self, params: dict) -> Protocol:
        domain_id = params["domain_id"]
        plugin_info = params["plugin_info"]

        self._check_plugin_info(plugin_info)
        _plugin = self._get_plugin(plugin_info)
        plugin_capability = _plugin.get("capability", {})

        if "supported_schema" in plugin_capability:
            params["capability"] = {
                "supported_schema": plugin_capability["supported_schema"]
            }
        else:
            raise ERROR_WRONG_PLUGIN_SETTINGS(key="capability.supported_schema")

        _LOGGER.debug(f'[create] capability: {params["capability"]}')
        _LOGGER.debug(f'[create] name: {params["name"]}')

        plugin_metadata, endpoint_info = self._init_plugin(plugin_info, domain_id)

        request_plugin = {
            "plugin_id": plugin_info["plugin_id"],
            "options": plugin_info.get("options", {}),
            "metadata": plugin_metadata,
        }

        if version := endpoint_info.get("updated_version", plugin_info.get("version")):
            request_plugin.update({"version": version})

        if "secret_data" in plugin_info:
            secret_mgr: SecretManager = self.locator.get_manager("SecretManager")
            secret_params = {
                "name": utils.generate_id("secret-noti-proto", 4),
                "data": plugin_info["secret_data"],
                "resource_group": "DOMAIN",
            }

            # if schema_id := plugin_info.get("schema_id"):
            #     secret_params["schema_id"] = schema_id
            # if provider := plugin_info.get("provider"):
            #     secret_params["provider"] = provider

            protocol_secret = secret_mgr.create_secret(secret_params)
            request_plugin.update(
                {
                    "secret_id": protocol_secret["secret_id"],
                    "schema": plugin_info["schema"],  # todo change to schema_id
                }
            )

        params["plugin_info"] = request_plugin
        protocol_vo: Protocol = self.protocol_mgr.create_protocol(params)

        return protocol_vo

    @transaction(permission="notification:Protocol.write", role_types=["DOMAIN_ADMIN"])
    @check_required(["protocol_id", "domain_id"])
    def update(self, params: dict):
        """Update protocol

        Args:
            params (dict): {
                'protocol_id': 'str',   # required
                'name': 'str',
                'tags': 'dict',
                'domain_id': 'str'      # injected from auth
            }

        Returns:
            protocol_vo (object)
        """

        domain_id = params["domain_id"]
        protocol_id = params["protocol_id"]

        protocol_vo = self.protocol_mgr.get_protocol(protocol_id, domain_id)

        if protocol_vo.protocol_type == "INTERNAL":
            raise ERROR_NOT_ALLOWED_UPDATE_PROTOCOL_TYPE(protocol_id=protocol_id)

        return self.protocol_mgr.update_protocol_by_vo(params, protocol_vo)

    @transaction(permission="notification:Protocol.write", role_types=["DOMAIN_ADMIN"])
    @check_required(["protocol_id", "domain_id"])
    def update_plugin(self, params: dict):
        """Update protocol plugin

        Args:
            params (dict): {
                'protocol_id': 'str',
                'version': 'str',
                'options': 'dict',
                'domain_id': 'str'
            }

        Returns:
            protocol_vo (object)
        """
        protocol_id = params["protocol_id"]
        domain_id = params["domain_id"]

        protocol_vo = self.protocol_mgr.get_protocol(protocol_id, domain_id)

        plugin_info = protocol_vo.plugin_info.to_dict()

        if plugin_info["upgrade_mode"] == "AUTO":
            plugin_metadata, endpoint_info = self._init_plugin(plugin_info, domain_id)

            plugin_info["metadata"] = plugin_metadata

            if version := endpoint_info.get("updated_version"):
                plugin_info["version"] = version
        else:
            if version := params.get("version"):
                # Update plugin_version
                plugin_id = plugin_info["plugin_id"]

                repo_mgr = self.locator.get_manager("RepositoryManager")
                repo_mgr.check_plugin_version(plugin_id, version)

                plugin_info["version"] = version
                plugin_info["metadata"] = self._init_plugin(plugin_info, domain_id)

        if options := params.get("options", {}):
            # Overwrite
            plugin_info["options"] = options

        params = {
            "protocol_id": protocol_id,
            "domain_id": domain_id,
            "plugin_info": plugin_info,
        }

        _LOGGER.debug(f"[update_plugin] {plugin_info}")
        return self.protocol_mgr.update_protocol_by_vo(params, protocol_vo)

    @transaction(permission="notification:Protocol.write", role_types=["DOMAIN_ADMIN"])
    @check_required(["protocol_id", "domain_id"])
    def delete(self, params: dict):
        """Delete protocol

        Args:
            params (dict): {
                'protocol_id': 'str',   # required
                'domain_id': 'str'      # injected from auth
            }

        Returns:
            None
        """
        protocol_id = params["protocol_id"]
        domain_id = params["domain_id"]

        protocol_vo: Protocol = self.protocol_mgr.get_protocol(protocol_id, domain_id)
        self.check_existed_channel_using_protocol(protocol_vo)

        if secret_id := protocol_vo.plugin_info.secret_id:
            secret_mgr: SecretManager = self.locator.get_manager("SecretManager")
            secret_mgr.delete_secret(secret_id)

        return self.protocol_mgr.delete_protocol_by_vo(protocol_vo)

    @transaction(permission="notification:Protocol.write", role_types=["DOMAIN_ADMIN"])
    @check_required(["protocol_id", "domain_id"])
    def enable(self, params: dict):
        """Enable protocol

        Args:
            params (dict): {
                'protocol_id': 'str',   # required
                'domain_id': 'str'      # injected from auth
            }

        Returns:
            protocol_vo (object)
        """
        protocol_vo = self.protocol_mgr.get_protocol(
            params["protocol_id"], params["domain_id"]
        )
        protocol_vo = self.protocol_mgr.enable_protocol(protocol_vo)
        return protocol_vo

    @transaction(permission="notification:Protocol.write", role_types=["DOMAIN_ADMIN"])
    @check_required(["protocol_id", "domain_id"])
    def disable(self, params):
        """Disable protocol

        Args:
            params (dict): {
                'protocol_id': 'str',   # required
                'domain_id': 'str'      # injected from auth
            }

        Returns:
            protocol_vo (object)
        """

        protocol_vo = self.protocol_mgr.get_protocol(
            params["protocol_id"], params["domain_id"]
        )
        protocol_vo = self.protocol_mgr.disable_protocol(protocol_vo)
        return protocol_vo

    @transaction(
        permission="notification:Protocol.read",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER", "WORKSPACE_MEMBER", "USER"],
    )
    @check_required(["protocol_id", "domain_id"])
    def get(self, params):
        """Get Protocol

        Args:
            params (dict): {
                'protocol_id': 'str',   # required
                'domain_id': 'str',     # injected from auth
            }

        Returns:
            domain_vo (object)
        """
        protocol_id = params["protocol_id"]
        domain_id = params["domain_id"]

        # Create Default Protocol if protocol is not exited
        self._create_default_protocol(domain_id)
        self._initialize_protocols(domain_id)

        return self.protocol_mgr.get_protocol(protocol_id, domain_id)

    @transaction(
        permission="notification:Protocol.read",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER", "WORKSPACE_MEMBER", "USER"],
    )
    @check_required(["domain_id"])
    @append_query_filter(["protocol_id", "name", "state", "protocol_type", "domain_id"])
    @append_keyword_filter(["protocol_id", "name"])
    def list(self, params: dict):
        """List protocol

        Args:
            params (dict): {
                'query': 'dict (spaceone.api.core.v1.Query)'
                'protocol_id': 'str',
                'name': 'str',
                'state': 'str',
                'protocol_type',
                'domain_id': 'str',                         # injected from auth
            }

        Returns:
            results (list): 'list of protocol_vo'
            total_count (int)
        """
        domain_id = params["domain_id"]
        query = params.get("query", {})

        # Create Default Protocol if protocol is not exited
        self._create_default_protocol(domain_id)
        self._initialize_protocols(domain_id)

        return self.protocol_mgr.list_protocols(query)

    @transaction(
        permission="notification:Protocol.read",
        role_types=["DOMAIN_ADMIN", "WORKSPACE_OWNER", "WORKSPACE_MEMBER", "USER"],
    )
    @check_required(["query", "domain_id"])
    @append_query_filter(["domain_id"])
    @append_keyword_filter(["protocol_id", "name"])
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
        return self.protocol_mgr.stat_protocols(query)

    def _get_plugin(self, plugin_info):
        plugin_id = plugin_info["plugin_id"]

        repo_mgr: RepositoryManager = self.locator.get_manager("RepositoryManager")
        plugin_info = repo_mgr.get_plugin(plugin_id)

        if version := plugin_info.get("version"):
            repo_mgr.check_plugin_version(plugin_id, version)

        return plugin_info

    def _init_plugin(self, plugin_info: dict, domain_id: str) -> Tuple[dict, dict]:
        options = plugin_info.get("options", {})

        plugin_mgr: PluginManager = self.locator.get_manager("PluginManager")
        endpoint_info = plugin_mgr.initialize(plugin_info, domain_id)
        metadata = plugin_mgr.init_plugin(options)

        return metadata, endpoint_info

    def check_existed_channel_using_protocol(self, protocol_vo):
        project_channel_mgr: ProjectChannelManager = self.locator.get_manager(
            "ProjectChannelManager"
        )
        user_channel_mgr: UserChannelManager = self.locator.get_manager(
            "UserChannelManager"
        )

        query = {
            "filter": [{"k": "protocol_id", "v": protocol_vo.protocol_id, "o": "eq"}]
        }

        (
            project_channel_vos,
            prj_ch_total_count,
        ) = project_channel_mgr.list_project_channels(query)
        user_channel_vos, user_ch_total_count = user_channel_mgr.list_user_channels(
            query
        )

        if prj_ch_total_count > 0 or user_ch_total_count > 0:
            raise EROR_DELETE_PROJECT_EXITED_CHANNEL(
                protocol_id=protocol_vo.protocol_id
            )

    @cache.cacheable(key="default-protocol:{domain_id}", expire=300)
    def _create_default_protocol(self, domain_id):
        _LOGGER.debug(f"[_create_default_protocol] domain_id: {domain_id}")

        query = {"filter": [{"k": "domain_id", "v": domain_id, "o": "eq"}]}
        protocol_vos, total_count = self.protocol_mgr.list_protocols(query)

        installed_protocol_names = [protocol_vo.name for protocol_vo in protocol_vos]
        _LOGGER.debug(
            f"[_create_default_protocol] Installed Plugins : {installed_protocol_names}"
        )

        for _protocol_data in DEFAULT_INTERNAL_PROTOCOLS:
            if _protocol_data["name"] not in installed_protocol_names:
                _LOGGER.debug(f'Create default protocol: {_protocol_data["name"]}')
                _protocol_data["domain_id"] = domain_id
                self.protocol_mgr.create_protocol(_protocol_data)

        return True

    @cache.cacheable(key="init-protocol:{domain_id}", expire=300)
    def _initialize_protocols(self, domain_id):
        _LOGGER.debug(f"[_initialize_protocol] domain_id: {domain_id}")

        query = {"filter": [{"k": "domain_id", "v": domain_id, "o": "eq"}]}
        protocol_vos, total_count = self.protocol_mgr.list_protocols(query)

        installed_protocol_ids = [
            protocol_vo.plugin_info.plugin_id for protocol_vo in protocol_vos
        ]
        _LOGGER.debug(
            f"[_initialize_protocol] Installed Plugins : {installed_protocol_ids}"
        )

        global_conf = config.get_global()
        for _protocol_data in global_conf.get("INSTALLED_PROTOCOL_PLUGINS", []):
            if _protocol_data["plugin_info"]["plugin_id"] not in installed_protocol_ids:
                try:
                    _LOGGER.debug(
                        f'[_initialize_protocol] Create init protocol: {_protocol_data["plugin_info"]["plugin_id"]}'
                    )
                    _protocol_data["domain_id"] = domain_id
                    self._create(_protocol_data)
                except Exception as e:
                    _LOGGER.error(f"[_initialize_protocol] {e}")

        return True

    @staticmethod
    def _check_plugin_info(plugin_info_params):
        if "plugin_id" not in plugin_info_params:
            raise ERROR_REQUIRED_PARAMETER(key="plugin_info.plugin_id")

        # Todo : modify schema to schema_id after migration
        if "secret_data" in plugin_info_params and "schema" not in plugin_info_params:
            raise ERROR_REQUIRED_PARAMETER(key="plugin_info.schema")

        if (
            "upgrade_mode" in plugin_info_params
            and plugin_info_params["upgrade_mode"] == "MANUAL"
        ):
            if "version" not in plugin_info_params:
                raise ERROR_REQUIRED_PARAMETER(key="plugin_info.version")
