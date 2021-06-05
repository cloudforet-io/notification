import logging

from spaceone.core.manager import BaseManager
from spaceone.notification.model.project_channel_model import ProjectChannel

_LOGGER = logging.getLogger(__name__)


class ProjectChannelManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.project_channel_model: ProjectChannel = self.locator.get_model('ProjectChannel')

    def create_project_channel(self, params):
        def _rollback(vo):
            _LOGGER.info(f'[create_project_channel._rollback] Delete Project Channel : {vo.name} ({vo.project_channel_id})')
            vo.delete()

        project_channel_vo: ProjectChannel = self.project_channel_model.create(params)

        self.transaction.add_rollback(_rollback, project_channel_vo)

        return project_channel_vo

    def update_project_channel(self, params):
        project_channel_vo = self.get_project_channel(params['project_channel_id'], params['domain_id'])
        return self.update_project_channel_by_vo(params, project_channel_vo)

    def update_project_channel_by_vo(self, params, project_channel_vo):
        def _rollback(old_data):
            _LOGGER.info(f'[update_project_channel._rollback] Revert Data : {old_data["name"]} '
                         f'({old_data["project_channel_id"]})')
            project_channel_vo.update(old_data)

        self.transaction.add_rollback(_rollback, project_channel_vo.to_dict())
        return project_channel_vo.update(params)

    def delete_project_channel(self, project_channel_id, domain_id):
        project_channel_vo: ProjectChannel = self.get_project_channel(project_channel_id, domain_id)
        self.delete_project_channel_by_vo(project_channel_vo)

    def enable_project_channel(self, project_channel_id, domain_id):
        def _rollback(old_data):
            _LOGGER.info(f'[enable_project_channel._rollback] '
                         f'Revert Data : {old_data["name"]} ({old_data["project_channel_id"]})')
            project_channel_vo.update(old_data)

        project_channel_vo: ProjectChannel = self.get_project_channel(project_channel_id, domain_id)

        if project_channel_vo.state != 'ENABLED':
            self.transaction.add_rollback(_rollback, project_channel_vo.to_dict())
            project_channel_vo.update({'state': 'ENABLED'})

        return project_channel_vo

    def disable_project_channel(self, project_channel_id, domain_id):
        def _rollback(old_data):
            _LOGGER.info(f'[disable_project_channel._rollback] '
                         f'Revert Data : {old_data["name"]} ({old_data["project_channel_id"]})')
            project_channel_vo.update(old_data)

        project_channel_vo: ProjectChannel = self.get_project_channel(project_channel_id, domain_id)

        if project_channel_vo.state != 'DISABLED':
            self.transaction.add_rollback(_rollback, project_channel_vo.to_dict())
            project_channel_vo.update({'state': 'DISABLED'})

        return project_channel_vo

    def get_project_channel(self, project_channel_id, domain_id, only=None):
        return self.project_channel_model.get(project_channel_id=project_channel_id, domain_id=domain_id, only=only)

    def list_project_channels(self, query):
        return self.project_channel_model.query(**query)

    def stat_project_channels(self, query):
        return self.project_channel_model.stat(**query)

    @staticmethod
    def delete_project_channel_by_vo(project_channel_vo):
        project_channel_vo.delete()