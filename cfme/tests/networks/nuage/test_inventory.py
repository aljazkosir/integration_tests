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
