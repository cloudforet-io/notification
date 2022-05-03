from spaceone.api.notification.v1 import notification_usage_pb2, notification_usage_pb2_grpc
from spaceone.core.pygrpc import BaseAPI


class NotificationUsage(BaseAPI, notification_usage_pb2_grpc.NotificationUsageServicer):

    pb2 = notification_usage_pb2
    pb2_grpc = notification_usage_pb2_grpc

    def list(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('NotificationUsageService', metadata) as notification_usage_svc:
            notification_usage_vos, total_count = notification_usage_svc.list(params)
            return self.locator.get_info('NotificationUsagesInfo',
                                         notification_usage_vos,
                                         total_count,
                                         minimal=self.get_minimal(params))

    def stat(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('NotificationUsageService', metadata) as notification_usage_svc:
            return self.locator.get_info('StatisticsInfo', notification_usage_svc.stat(params))
