import functools

from spaceone.api.notification.v1 import notification_usage_pb2
from spaceone.notification.model.notification_usage_model import NotificationUsage

__all__ = ['NotificationUsageInfo', 'NotificationUsagesInfo']


def NotificationUsageInfo(noti_usage_vo: NotificationUsage, minimal=False):
    info = {
        'protocol_id': noti_usage_vo.protocol_id,
        'usage_month': noti_usage_vo.usage_month,
        'usage_date': noti_usage_vo.usage_date,
        'count': noti_usage_vo.count,
        'fail_count': noti_usage_vo.fail_count,
        'domain_id': noti_usage_vo.domain_id
    }

    return notification_usage_pb2.NotificationUsageInfo(**info)


def NotificationUsagesInfo(noti_usage_vos, total_count, **kwargs):
    results = list(map(functools.partial(NotificationUsageInfo, **kwargs), noti_usage_vos))
    return notification_usage_pb2.NotificationUsagesInfo(results=results, total_count=total_count)
