from spaceone.api.notification.v1 import notification_pb2, notification_pb2_grpc
from spaceone.core.pygrpc import BaseAPI


class Notification(BaseAPI, notification_pb2_grpc.NotificationServicer):

    pb2 = notification_pb2
    pb2_grpc = notification_pb2_grpc

    def create(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('NotificationService', metadata) as notification_svc:
            notification_svc.create(params)
            return self.locator.get_info('EmptyInfo')

    def push(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('NotificationService', metadata) as notification_svc:
            notification_svc.push(params)
            return self.locator.get_info('EmptyInfo')

    def delete(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('NotificationService', metadata) as notification_svc:
            notification_svc.delete(params)
            return self.locator.get_info('EmptyInfo')

    def delete_all(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('NotificationService', metadata) as notification_svc:
            notification_svc.delete_all(params)
            return self.locator.get_info('EmptyInfo')

    def set_read(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('NotificationService', metadata) as notification_svc:
            notification_svc.set_read(params)
            return self.locator.get_info('EmptyInfo')

    def get(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('NotificationService', metadata) as notification_svc:
            return self.locator.get_info('NotificationInfo', notification_svc.get(params))

    def list(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('NotificationService', metadata) as notification_svc:
            notification_vos, total_count = notification_svc.list(params)
            return self.locator.get_info('NotificationsInfo',
                                         notification_vos,
                                         total_count,
                                         minimal=self.get_minimal(params))

    def stat(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('NotificationService', metadata) as notification_svc:
            return self.locator.get_info('StatisticsInfo', notification_svc.stat(params))
