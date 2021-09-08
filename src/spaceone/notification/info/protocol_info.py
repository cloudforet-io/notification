import functools

from spaceone.api.notification.v1 import protocol_pb2
from spaceone.core.pygrpc.message_type import *
from spaceone.core import utils
from spaceone.notification.model.protocol_model import Protocol

__all__ = ['ProtocolInfo', 'ProtocolsInfo']


def PluginInfo(plugin_info):
    if plugin_info:
        info = {
            'plugin_id': plugin_info.plugin_id,
            'version': plugin_info.version,
            'options': change_struct_type(plugin_info.options),
            'metadata': change_struct_type(plugin_info.metadata),
            'secret_id': plugin_info.secret_id,
            'upgrade_mode': plugin_info.upgrade_mode
        }
        return protocol_pb2.PluginInfo(**info)
    return None


def ProtocolInfo(protocol_vo: Protocol, minimal=False):
    info = {
        'protocol_id': protocol_vo.protocol_id,
        'name': protocol_vo.name,
        'state': protocol_vo.state
    }

    if not minimal:
        info.update({
            'capability': change_struct_type(protocol_vo.capability),
            'protocol_type': protocol_vo.protocol_type,
            'resource_type': protocol_vo.resource_type,
            'plugin_info': PluginInfo(protocol_vo.plugin_info),
            'created_at': utils.datetime_to_iso8601(protocol_vo.created_at),
            'tags': change_struct_type(protocol_vo.tags),
            'domain_id': protocol_vo.domain_id
        })

    return protocol_pb2.ProtocolInfo(**info)


def ProtocolsInfo(protocol_vos, total_count, **kwargs):
    results = list(map(functools.partial(ProtocolInfo, **kwargs), protocol_vos))

    return protocol_pb2.ProtocolsInfo(results=results, total_count=total_count)

