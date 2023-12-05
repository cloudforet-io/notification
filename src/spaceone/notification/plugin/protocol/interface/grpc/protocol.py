from spaceone.core.pygrpc import BaseAPI
from spaceone.api.notification.plugin import protocol_pb2, protocol_pb2_grpc
from spaceone.notification.plugin.protocol.service.protocol_service import ProtocolService


class Protocol(BaseAPI, protocol_pb2_grpc.ProtocolServicer):
    pb2 = protocol_pb2
    pb2_grpc = protocol_pb2_grpc

    def init(self, request, context):
        params, metadata = self.parse_request(request, context)
        protocol_svc = ProtocolService(metadata)
        response: dict = protocol_svc.init(params)
        return self.dict_to_message(response)

    def verify(self, request, context):
        params, metadata = self.parse_request(request, context)
        protocol_svc = ProtocolService(metadata)
        protocol_svc.verify(params)
        return self.empty()
