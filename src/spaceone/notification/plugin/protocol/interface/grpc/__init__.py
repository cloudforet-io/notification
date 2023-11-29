from spaceone.core.pygrpc.server import GRPCServer
from spaceone.notification.plugin.protocol.interface.grpc.protocol import Protocol
from spaceone.notification.plugin.protocol.interface.grpc.notification import Notification

_all_ = ['app']

app = GRPCServer()
app.add_service(Protocol)
app.add_service(Notification)
