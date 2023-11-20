from spaceone.core.pygrpc import BaseAPI
from spaceone.api.notification.plugin import notification_pb2, notification_pb2_grpc
from spaceone.notification.plugin.protocol.error.response import *
from spaceone.notification.plugin.protocol.service.notification_service import NotificationService



class Notification(BaseAPI, notification_pb2_grpc.NotificationServicer):
    pb2 = notification_pb2
    pb2_grpc = notification_pb2_grpc

    def dispatch(self, request, context):
        params, metadata = self.parse_request(request, context)
        notification_svc = NotificationService(metadata)
        for response in notification_svc.dispatch(params):
            # response = self._select_valid_resource_and_resource_type(response)

            # if response['state'] == 'FAILURE':
            #     response['resource_type'] = 'notification.ErrorResource'
            #
            # if 'error_message' in response:
            #     error_message = response.pop('error_message')
            #     response['message'] = error_message
            #
            # if 'match_keys' in response:
            #     match_keys = response.pop('match_keys')
            #     response['match_rules'] = {}
            #
            #     for idx, keys in enumerate(match_keys, 1):
            #         response['match_rules'][str(idx)] = keys

            yield self.dict_to_message(response)

    # def _select_valid_resource_and_resource_type(self, response: dict) -> dict:
    #     resources = list(VALID_RESOURCE_TYPES.keys())
    #     valid_resource = [key for key in response.keys() if key in resources and response[key]]
    #
    #     self._check_resource_and_resource_type(valid_resource, response)
    #
    #     resources.remove(valid_resource[0])
    #     for key in resources:
    #         del response[key]
    #
    #     return response
    #
    # @staticmethod
    # def _check_resource_and_resource_type(valid_resource, response) -> None:
    #     if not len(valid_resource):
    #         raise ERROR_NO_INPUT_FIELD()
    #
    #     if len(valid_resource) != 1:
    #         raise ERROR_INVAILD_INPUT_FIELD(fields=valid_resource)
    #
    #     resource_type = response['resource_type']
    #     if resource_type != VALID_RESOURCE_TYPES[valid_resource[0]]:
    #         raise ERROR_NOT_MATCH_RESOURCE_TYPE(resource_type=resource_type, resource=valid_resource[0])