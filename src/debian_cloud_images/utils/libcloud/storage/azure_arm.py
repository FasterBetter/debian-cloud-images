from libcloud.common.base import BaseDriver
from urllib.parse import urlparse

from ..common.azure import AzureGenericOAuth2Connection
from .azure_blobs import AzureBlobsOAuth2StorageDriver


class AzureResourceManagementStorageDriver(BaseDriver):
    connectionCls = AzureGenericOAuth2Connection
    name = 'Azure Storage Accounts'
    website = 'https://azure.microsoft.com/en-us/services/storage/'

    def __init__(self, *, client_id, client_secret, subscription_id, tenant_id):
        self.client_id = client_id
        self.client_secret = client_secret
        self.subscription_id = subscription_id
        self.tenant_id = tenant_id

        super().__init__(key='', secret='')

    def _ex_connection_class_kwargs(self):
        ret = super()._ex_connection_class_kwargs()
        ret.update({
            'host': 'management.azure.com',
            'login_resource': 'https://management.core.windows.net/',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'tenant_id': self.tenant_id,
        })
        return ret

    def get_storage(self, resource_group=None, name=None, _id=None):
        if not _id:
            _id = '/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Storage/storageAccounts/{}'.format(
                self.subscription_id,
                resource_group,
                name,
            )

        r = self.connection.request(_id, params={'api-version': '2018-07-01'})

        endpoint = urlparse(r.object['properties']['primaryEndpoints']['blob'])

        return AzureBlobsOAuth2StorageDriver(
            name,
            client_id=self.client_id,
            client_secret=self.client_secret,
            tenant_id=self.tenant_id,
            host=endpoint.netloc,
            extra=r.object,
        )
