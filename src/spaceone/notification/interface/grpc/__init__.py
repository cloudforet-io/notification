from spaceone.core.pygrpc.server import GRPCServer
from spaceone.notification.interface.grpc.protocol import Protocol
from spaceone.notification.interface.grpc.user_channel import UserChannel
from spaceone.notification.interface.grpc.project_channel import ProjectChannel
from spaceone.notification.interface.grpc.notification import Notification

_all_ = ['app']

app = GRPCServer()
app.add_service(Protocol)
app.add_service(UserChannel)
app.add_service(ProjectChannel)
app.add_service(Notification)
