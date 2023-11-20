from spaceone.notification.plugin.protocol.lib.server import ProtocolPluginServer

app = ProtocolPluginServer()


@app.route('Protocol.init')
def protocol_init(params: dict) -> dict:
    """ init plugin by options

    Args:
        params (ProtocolInitRequest): {
            'options': 'dict',    # Required
            'domain_id': 'str'
        }

    Returns:
        PluginResponse: {
            'metadata': 'dict'
        }
    """
    return {'metadata': {}}


@app.route('Protocol.verify')
def protocol_verify(params: dict) -> None:
    """ Verifying protocol plugin

    Args:
        params (ProtocolVerifyRequest): {
            'options': 'dict',      # Required
            'secret_data': 'dict',  # Required
            'domain_id': 'str'
        }

    Returns:
        None
    """
    pass


@app.route('Notification.dispatch')
def notification_dispatch(params: dict) -> dict:
    """ dispatch notification

    Args:
        params (NotificationDispatchRequest): {
            'options': 'dict',      # Required
            'secret_data': 'dict',  # Required
            'channel_data': 'dict', # Required
            'message': 'dict',
            'notification_type': 'str',
        }

    Returns:
        Generator[ResourceResponse, None, None]
        {
            'notificiation_type': 'INFO | ERROR | SUCCESS | WARNING',
            'message': dict
        }
    """
    pass
