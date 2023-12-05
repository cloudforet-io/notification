from spaceone.api.notification.v1 import quota_pb2, quota_pb2_grpc
from spaceone.core.pygrpc import BaseAPI


class Quota(BaseAPI, quota_pb2_grpc.QuotaServicer):

    pb2 = quota_pb2
    pb2_grpc = quota_pb2_grpc

    def create(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('QuotaService', metadata) as quota_svc:
            return self.locator.get_info('QuotaInfo', quota_svc.create(params))

    def update(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('QuotaService', metadata) as quota_svc:
            return self.locator.get_info('QuotaInfo', quota_svc.update(params))

    def delete(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('QuotaService', metadata) as quota_svc:
            quota_svc.delete(params)
            return self.locator.get_info('EmptyInfo')

    def get(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('QuotaService', metadata) as quota_svc:
            return self.locator.get_info('QuotaInfo', quota_svc.get(params))

    def list(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('QuotaService', metadata) as quota_svc:
            quota_vos, total_count = quota_svc.list(params)
            return self.locator.get_info('QuotasInfo',
                                         quota_vos,
                                         total_count,
                                         minimal=self.get_minimal(params))

    def stat(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service('QuotaService', metadata) as quota_svc:
            return self.locator.get_info('StatisticsInfo', quota_svc.stat(params))
