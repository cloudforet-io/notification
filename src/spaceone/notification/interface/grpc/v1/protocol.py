from spaceone.api.notification.v1 import protocol_pb2, protocol_pb2_grpc
from spaceone.core.pygrpc import BaseAPI


class Protocol(BaseAPI, protocol_pb2_grpc.ProtocolServicer):

    pb2 = protocol_pb2
    pb2_grpc = protocol_pb2_grpc

    def create(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('ProtocolService', metadata) as protocol_svc:
            return self.locator.get_info('ProtocolInfo', protocol_svc.create(params))

    def update(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('ProtocolService', metadata) as protocol_svc:
            return self.locator.get_info('ProtocolInfo', protocol_svc.update(params))

    def update_plugin(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('ProtocolService', metadata) as protocol_svc:
            return self.locator.get_info('ProtocolInfo', protocol_svc.update_plugin(params))

    def delete(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('ProtocolService', metadata) as protocol_svc:
            protocol_svc.delete(params)
            return self.locator.get_info('EmptyInfo')

    def enable(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('ProtocolService', metadata) as protocol_svc:
            return self.locator.get_info('ProtocolInfo', protocol_svc.enable(params))

    def disable(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('ProtocolService', metadata) as protocol_svc:
            return self.locator.get_info('ProtocolInfo', protocol_svc.disable(params))

    def get(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('ProtocolService', metadata) as protocol_svc:
            return self.locator.get_info('ProtocolInfo', protocol_svc.get(params))

    def list(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('ProtocolService', metadata) as protocol_svc:
            protocol_vos, total_count = protocol_svc.list(params)
            return self.locator.get_info('ProtocolsInfo',
                                         protocol_vos,
                                         total_count,
                                         minimal=self.get_minimal(params))

    def stat(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('ProtocolService', metadata) as protocol_svc:
            return self.locator.get_info('StatisticsInfo', protocol_svc.stat(params))
