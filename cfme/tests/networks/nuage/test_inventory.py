import pytest

from cfme.networks.provider.nuage import NuageProvider

pytestmark = [
    pytest.mark.provider([NuageProvider], scope='module')
]


def test_tenant_details(setup_provider_modscope, provider, with_nuage_sandbox_modscope):
    sandbox = with_nuage_sandbox_modscope
    tenant_name = sandbox['enterprise'].name
    tenant = provider.collections.cloud_tenants.instantiate(name=tenant_name)

    tenant.validate_stats({
        'num_cloud_subnets': 2,
        'num_network_routers': 1,
        'num_security_groups': 2,
        'num_network_ports': 4
    })


def test_subnet_details(setup_provider_modscope, provider, with_nuage_sandbox_modscope):
    """
    Ensure L3 subnet details displays expected info.

    L3 subnets are always connected to routers, hence we navigate to them as
      Tenant > Router > Subnet
    """
    sandbox = with_nuage_sandbox_modscope
    tenant_name = sandbox['enterprise'].name
    subnet_name = sandbox['subnet'].name
    router_name = sandbox['domain'].name
    tenant = provider.collections.cloud_tenants.instantiate(name=tenant_name)
    router = tenant.collections.routers.instantiate(name=router_name)
    subnet = router.collections.subnets.instantiate(name=subnet_name)

    subnet.validate_stats({
        'name': subnet_name,
        'type': 'ManageIQ/Providers/Nuage/Network Manager/Cloud Subnet/L3',
        'cidr': '192.168.0.0/24',
        'gateway': '192.168.0.1',
        'network_protocol': 'ipv4',
        'network_router': router_name,
        'num_network_ports': 2,
        'num_security_groups': 0
    })


def test_l2_subnet_details(setup_provider_modscope, provider, with_nuage_sandbox_modscope):
    """
    Ensure L2 subnet details displays expected info.

    L2 subnets act as standalone and are thus not connected to any router.
    We navigate to them as
      Tenant > Subnet
    """
    sandbox = with_nuage_sandbox_modscope
    tenant_name = sandbox['enterprise'].name
    subnet_name = sandbox['l2_domain'].name
    tenant = provider.collections.cloud_tenants.instantiate(name=tenant_name)
    subnet = tenant.collections.subnets.instantiate(name=subnet_name)

    subnet.validate_stats({
        'name': subnet_name,
        'type': 'ManageIQ/Providers/Nuage/Network Manager/Cloud Subnet/L2',
        'num_network_ports': 2,
        'num_security_groups': 1
    })
