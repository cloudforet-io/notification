import functools

from spaceone.api.notification.v1 import quota_pb2
from spaceone.core.pygrpc.message_type import *
from spaceone.notification.model.quota_model import Quota

__all__ = ['QuotaInfo', 'QuotasInfo']


def QuotaInfo(quota_vo: Quota, minimal=False):
    info = {
        'quota_id': quota_vo.quota_id,
        'protocol_id': quota_vo.protocol_id,
        'domain_id': quota_vo.domain_id
    }

    if not minimal:
        info.update({'limit': change_struct_type(quota_vo.limit)})

    return quota_pb2.QuotaInfo(**info)


def QuotasInfo(quota_vos, total_count, **kwargs):
    results = list(map(functools.partial(QuotaInfo, **kwargs), quota_vos))
    return quota_pb2.QuotasInfo(results=results, total_count=total_count)
