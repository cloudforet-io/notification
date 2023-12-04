from spaceone.core.pygrpc import BaseAPI
from spaceone.api.notification.plugin import notification_pb2, notification_pb2_grpc
from spaceone.notification.plugin.protocol.service.notification_service import NotificationService


class Notification(BaseAPI, notification_pb2_grpc.NotificationServicer):
    pb2 = notification_pb2
    pb2_grpc = notification_pb2_grpc

    def dispatch(self, request, context):
        params, metadata = self.parse_request(request, context)
        notification_svc = NotificationService(metadata)
        notification_svc.dispatch(params)
        return self.empty()
