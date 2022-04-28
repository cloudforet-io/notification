import functools

from spaceone.api.notification.v1 import notification_pb2
from spaceone.core.pygrpc.message_type import *
from spaceone.core import utils
from spaceone.notification.model.notification_model import Notification

__all__ = ['NotificationInfo', 'NotificationsInfo']


def NotificationInfo(notification_vo: Notification, minimal=False):
    info = {
        'notification_id': notification_vo.notification_id,
        'topic': notification_vo.topic,
        'notification_type': notification_vo.notification_type,
        'notification_level': notification_vo.notification_level
    }

    if not minimal:

        if notification_vo.user_id:
            info.update({'user_id': notification_vo.user_id})

        info.update({
            'message': change_struct_type(notification_vo.message),
            'is_read': notification_vo.is_read,
            'created_at': utils.datetime_to_iso8601(notification_vo.created_at),
            'domain_id': notification_vo.domain_id
        })

    return notification_pb2.NotificationInfo(**info)


def NotificationsInfo(notification_vos, total_count, **kwargs):
    results = list(map(functools.partial(NotificationInfo, **kwargs), notification_vos))
    return notification_pb2.NotificationsInfo(results=results, total_count=total_count)
