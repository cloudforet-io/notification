from spaceone.api.notification.v1 import project_channel_pb2, project_channel_pb2_grpc
from spaceone.core.pygrpc import BaseAPI


class ProjectChannel(BaseAPI, project_channel_pb2_grpc.ProjectChannelServicer):

    pb2 = project_channel_pb2
    pb2_grpc = project_channel_pb2_grpc

    def create(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('ProjectChannelService', metadata) as project_channel_svc:
            return self.locator.get_info('ProjectChannelInfo', project_channel_svc.create(params))

    def update(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('ProjectChannelService', metadata) as project_channel_svc:
            return self.locator.get_info('ProjectChannelInfo', project_channel_svc.update(params))

    def set_schedule(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('ProjectChannelService', metadata) as project_channel_svc:
            return self.locator.get_info('ProjectChannelInfo', project_channel_svc.set_schedule(params))

    def set_subscription(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('ProjectChannelService', metadata) as project_channel_svc:
            return self.locator.get_info('ProjectChannelInfo', project_channel_svc.set_subscription(params))

    def delete(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('ProjectChannelService', metadata) as project_channel_svc:
            project_channel_svc.delete(params)
            return self.locator.get_info('EmptyInfo')

    def enable(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('ProjectChannelService', metadata) as project_channel_svc:
            return self.locator.get_info('ProjectChannelInfo', project_channel_svc.enable(params))

    def disable(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('ProjectChannelService', metadata) as project_channel_svc:
            return self.locator.get_info('ProjectChannelInfo', project_channel_svc.disable(params))

    def get(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('ProjectChannelService', metadata) as project_channel_svc:
            return self.locator.get_info('ProjectChannelInfo', project_channel_svc.get(params))

    def list(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('ProjectChannelService', metadata) as project_channel_svc:
            project_channel_vos, total_count = project_channel_svc.list(params)
            return self.locator.get_info('ProjectChannelsInfo',
                                         project_channel_vos,
                                         total_count,
                                         minimal=self.get_minimal(params))

    def stat(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('ProjectChannelService', metadata) as project_channel_svc:
            return self.locator.get_info('StatisticsInfo', project_channel_svc.stat(params))
