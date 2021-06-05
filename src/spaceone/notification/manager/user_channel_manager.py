import logging

from spaceone.core.manager import BaseManager
from spaceone.notification.model.user_channel_model import UserChannel

_LOGGER = logging.getLogger(__name__)


class UserChannelManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_channel_model: UserChannel = self.locator.get_model('UserChannel')

    def create_user_channel(self, params):
        def _rollback(vo):
            _LOGGER.info(f'[create_user_channel._rollback] Delete User Channel : {vo.name} ({vo.user_channel_id})')
            vo.delete()

        user_channel_vo: UserChannel = self.user_channel_model.create(params)

        self.transaction.add_rollback(_rollback, user_channel_vo)

        return user_channel_vo

    def update_user_channel(self, params):
        user_channel_vo = self.get_user_channel(params['user_channel_id'], params['domain_id'])
        return self.update_user_channel_by_vo(params, user_channel_vo)

    def update_user_channel_by_vo(self, params, user_channel_vo):
        def _rollback(old_data):
            _LOGGER.info(f'[user_user_channel._rollback] '
                         f'Revert Data : {old_data["name"]} '
                         f'({old_data["user_channel_id"]})')
            user_channel_vo.update(old_data)

        self.transaction.add_rollback(_rollback, user_channel_vo.to_dict())
        return user_channel_vo.update(params)

    def delete_user_channel(self, user_channel_id, domain_id):
        user_channel_vo: UserChannel = self.get_user_channel(user_channel_id, domain_id)
        self.delete_user_channel_by_vo(user_channel_vo)

    def enable_user_channel(self, user_channel_id, domain_id):
        def _rollback(old_data):
            _LOGGER.info(f'[enable_user_channel._rollback] '
                         f'Revert Data : {old_data["name"]} ({old_data["user_channel_id"]})')
            user_channel_vo.update(old_data)

        user_channel_vo: UserChannel = self.get_user_channel(user_channel_id, domain_id)

        if user_channel_vo.state != 'ENABLED':
            self.transaction.add_rollback(_rollback, user_channel_vo.to_dict())
            user_channel_vo.update({'state': 'ENABLED'})

        return user_channel_vo

    def disable_user_channel(self, user_channel_id, domain_id):
        def _rollback(old_data):
            _LOGGER.info(f'[disable_user_channel._rollback] '
                         f'Revert Data : {old_data["name"]} ({old_data["user_channel_id"]})')
            user_channel_vo.update(old_data)

        user_channel_vo: UserChannel = self.get_user_channel(user_channel_id, domain_id)

        if user_channel_vo.state != 'DISABLED':
            self.transaction.add_rollback(_rollback, user_channel_vo.to_dict())
            user_channel_vo.update({'state': 'DISABLED'})

        return user_channel_vo

    def get_user_channel(self, user_channel_id, domain_id, only=None):
        return self.user_channel_model.get(user_channel_id=user_channel_id, domain_id=domain_id, only=only)

    def list_user_channels(self, query):
        return self.user_channel_model.query(**query)

    def stat_user_channels(self, query):
        return self.user_channel_model.stat(**query)

    @staticmethod
    def delete_user_channel_by_vo(user_channel_vo):
        user_channel_vo.delete()