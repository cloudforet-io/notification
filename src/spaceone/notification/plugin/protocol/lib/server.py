from spaceone.core.pygrpc.server import GRPCServer
from spaceone.core.plugin.server import PluginServer
from spaceone.notification.plugin.protocol.interface.grpc import app
from spaceone.notification.plugin.protocol.service.notification_service import NotificationService
from spaceone.notification.plugin.protocol.service.protocol_service import ProtocolService

__all__ = ['ProtocolPluginServer']


class ProtocolPluginServer(PluginServer):
    _grpc_app: GRPCServer = app
    _global_conf_path: str = 'spaceone.notification.plugin.protocol.conf.global_conf:global_conf'
    _plugin_methods = {
        'Protocol': {
            'service': ProtocolService,
            'methods': ['init', 'verify']
        },
        'Notification': {
            'service': NotificationService,
            'methods': ['dispatch']
        }
    }
