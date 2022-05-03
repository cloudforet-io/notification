import logging
from spaceone.core.manager import BaseManager
from spaceone.notification.model.quota_model import Quota

_LOGGER = logging.getLogger(__name__)


class QuotaManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.quota_model: Quota = self.locator.get_model('Quota')

    def create_quota(self, params):
        def _rollback(quota_vo):
            _LOGGER.info(f'[create_quota._rollback]'
                         f'Delete Quota : {quota_vo.quota_id}'
                         f'({quota_vo.quota_id})')
            quota_vo.delete()

        quota_vo: Quota = self.quota_model.create(params)
        self.transaction.add_rollback(_rollback, quota_vo)

        return quota_vo

    def update_quota(self, params):
        quota_vo: Quota = self.get_quota(params['quota_id'], params['domain_id'])
        return self.update_quota_by_vo(params, quota_vo)

    def update_quota_by_vo(self, params, quota_vo):
        def _rollback(old_data):
            _LOGGER.info(f'[update_quota_by_vo._rollback] Revert Data : '
                         f'{old_data["quota_id"]}')
            quota_vo.update(old_data)

        self.transaction.add_rollback(_rollback, quota_vo.to_dict())
        return quota_vo.update(params)

    def delete_quota(self, quota_id, domain_id):
        self.delete_quota_by_vo(self.get_quota(quota_id, domain_id))

    def get_quota(self, quota_id, domain_id, only=None):
        return self.quota_model.get(quota_id=quota_id, domain_id=domain_id, only=only)

    def list_quotas(self, query={}):
        return self.quota_model.query(**query)

    def stat_quotas(self, query):
        return self.quota_model.stat(**query)

    @staticmethod
    def delete_quota_by_vo(quota_vo):
        return quota_vo.delete()

