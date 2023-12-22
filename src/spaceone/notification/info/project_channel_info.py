import functools

from spaceone.api.notification.v1 import project_channel_pb2
from spaceone.core.pygrpc.message_type import *
from spaceone.core import utils
from spaceone.notification.model.project_channel_model import ProjectChannel

__all__ = ["ProjectChannelInfo", "ProjectChannelsInfo"]


def ScheduleInfo(schedule_info):
    info = {
        "day_of_week": schedule_info.day_of_week,
        "start_hour": schedule_info.start_hour,
        "end_hour": schedule_info.end_hour,
    }
    return project_channel_pb2.ProjectChannelSchedule(**info)


def ProjectChannelInfo(project_channel_vo: ProjectChannel, minimal=False):
    info = {
        "project_channel_id": project_channel_vo.project_channel_id,
        "name": project_channel_vo.name,
        "state": project_channel_vo.state,
        "workspace_id": project_channel_vo.workspace_id,
    }

    if not minimal:
        info.update(
            {
                "data": change_struct_type(project_channel_vo.data),
                "secret_id": project_channel_vo.secret_id,
                "is_subscribe": project_channel_vo.is_subscribe,
                "subscriptions": change_list_value_type(
                    project_channel_vo.subscriptions
                ),
                "notification_level": project_channel_vo.notification_level,
                "protocol_id": project_channel_vo.protocol_id,
                "project_id": project_channel_vo.project_id,
                "is_scheduled": project_channel_vo.is_scheduled,
                "schedule": ScheduleInfo(project_channel_vo.schedule)
                if project_channel_vo.schedule
                else project_channel_vo.schedule,
                "created_at": utils.datetime_to_iso8601(project_channel_vo.created_at),
                "tags": change_struct_type(project_channel_vo.tags),
                "domain_id": project_channel_vo.domain_id,
            }
        )

    return project_channel_pb2.ProjectChannelInfo(**info)


def ProjectChannelsInfo(project_channel_vos, total_count, **kwargs):
    results = list(
        map(functools.partial(ProjectChannelInfo, **kwargs), project_channel_vos)
    )
    return project_channel_pb2.ProjectChannelsInfo(
        results=results, total_count=total_count
    )
