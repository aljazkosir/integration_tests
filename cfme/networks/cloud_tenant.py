import attr
from navmazing import NavigateToSibling

from cfme.cloud.tenant import TenantDetailsView
from cfme.common import Taggable
from cfme.exceptions import DestinationNotFound
from cfme.modeling.base import BaseCollection, BaseEntity, parent_of_type
from cfme.networks import ValidateStatsMixin
from cfme.networks.network_router import NetworkRouterCollection
from cfme.networks.subnet import SubnetCollection
from cfme.networks.views import ParentWithSubnetView, OneTenantNetworkRouterView
from cfme.utils import version
from cfme.utils.appliance.implementations.ui import navigator, CFMENavigateStep, navigate_to


@attr.s
class CloudTenant(Taggable, BaseEntity, ValidateStatsMixin):
    """Class representing cloud tenants"""
    in_version = ('5.10', version.LATEST)
    category = "networks"
    string_name = 'CloudTenant'
    quad_name = None
    db_types = ["CloudTenant"]

    _collections = {
        'subnets': SubnetCollection,
        'routers': NetworkRouterCollection
    }

    name = attr.ib()
    provider_obj = attr.ib(default=None)

    @property
    def provider(self):
        from cfme.networks.provider import NetworkProvider
        return parent_of_type(self, NetworkProvider)

    @property
    def num_cloud_subnets(self):
        view = navigate_to(self, "Details")
        return int(view.entities.relationships.get_text_of("Cloud Subnets"))

    @property
    def num_network_routers(self):
        view = navigate_to(self, "Details")
        return int(view.entities.relationships.get_text_of("Network Routers"))

    @property
    def num_security_groups(self):
        view = navigate_to(self, "Details")
        return int(view.entities.relationships.get_text_of("Security Groups"))

    @property
    def num_network_ports(self):
        view = navigate_to(self, "Details")
        return int(view.entities.relationships.get_text_of("Network Ports"))


@attr.s
class CloudTenantCollection(BaseCollection):
    """Collection object for CloudTenant object"""
    ENTITY = CloudTenant

    def all(self):
        view = navigate_to(self.filters.get('parent'), 'CloudTenants')
        cloud_tenants = view.entities.get_all(surf_pages=True)
        return [self.instantiate(name=s.name) for s in cloud_tenants]


@navigator.register(CloudTenant, 'Details')
class Details(CFMENavigateStep):
    VIEW = TenantDetailsView

    def prerequisite(self, *args, **kwargs):
        """Navigate through provider if it exists else navigate through parent object"""
        if self.obj.provider:
            return navigate_to(self.obj.provider, 'CloudTenants')
        else:
            return navigate_to(self.obj.parent, 'CloudTenants')

    def step(self):
        self.prerequisite_view.entities.get_entity(name=self.obj.name, surf_pages=True).click()


@navigator.register(CloudTenant, 'CloudSubnets')
class CloudSubnets(CFMENavigateStep):
    VIEW = ParentWithSubnetView
    prerequisite = NavigateToSibling('Details')

    def step(self):
        item = 'Cloud Subnets'
        if not int(self.prerequisite_view.entities.relationships.get_text_of(item)):
            raise DestinationNotFound("This Cloud Tenant doesn't have {item}".format(item=item))

        self.prerequisite_view.entities.relationships.click_at(item)


@navigator.register(CloudTenant, 'NetworkRouters')
class NetworkRouters(CFMENavigateStep):
    VIEW = OneTenantNetworkRouterView
    prerequisite = NavigateToSibling('Details')

    def step(self):
        item = 'Network Routers'
        if not int(self.prerequisite_view.entities.relationships.get_text_of(item)):
            raise DestinationNotFound("This Cloud Tenant doesn't have {item}".format(item=item))

        self.prerequisite_view.entities.relationships.click_at(item)
