from spaceone.core.error import *


class ERROR_INVALID_PLUGIN_VERSION(ERROR_INVALID_ARGUMENT):
    _message = 'Plugin version is invalid. (plugin_id = {plugin_id}, version = {version})'


class ERROR_NOT_FOUND_PLUGIN_VERSION(ERROR_BASE):
    _message = 'Not Found Plugin version (plugin_id= {plugin_id})'


class ERROR_SUPPORTED_SECRETS_NOT_EXISTS(ERROR_INVALID_ARGUMENT):
    _message = 'There are no secrets that support plugins. (plugin_id = {plugin_id}, provider = {provider})'


class ERROR_RESOURCE_SECRETS_NOT_EXISTS(ERROR_INVALID_ARGUMENT):
    _message = 'There are no secrets in the resources. (resource_id = {resource_id})'


class ERROR_WRONG_PLUGIN_SETTINGS(ERROR_BASE):
    _message = "The plugin settings is incorrect. (key = {key})"


class ERROR_NOT_ALLOWED_UPDATE_PROTOCOL_TYPE(ERROR_BASE):
    _message = 'default porotocol type is not allowed to update. (protocol_id = {protocol_id})'


class EROR_DELETE_PROJECT_EXITED_CHANNEL(ERROR_BASE):
    _message = '{protocol_id} was used in Project or User Channel'