# -*- coding: utf-8 -*-
"""This module tests Nuage EMS events."""
import pytest

from cfme.fixtures.nuage import create_basic_sandbox
from cfme.networks.provider.nuage import NuageProvider
from cfme.utils.log import logger

pytestmark = [
    pytest.mark.provider([NuageProvider])
]


def test_creating_entities_emits_events(register_event, networks_provider):
    """
    Tests whether EMS events are emitted by Nuage server and recieved by MIQ. Here we test events
    that should be triggered upon entity creation. For example, when a new subnet is created on
    Nuage server, event of type 'nuage_subnet_create' should be emitted.

    Prerequisities:
        * A network provider that is set up and listening to events.

    Steps:
        * Deploy some entities outside of MIQ (directly in the provider)
        * Verify that expected events were captured by MIQ

    Important: register_event fixture must be listed before with_nuage_sandbox fixture because we
        need to start collecting events before we actually create the entities.

    Polarion:
        assignee: rhcf3_machine
        initialEstimate: 1/4h
    """
    listener = register_event
    name_prefix = 'integration-tests-events'

    expect_event(listener, name_prefix, 'nuage_enterprise_create')
    expect_event(listener, name_prefix,  'nuage_domaintemplate_create')
    expect_event(listener, name_prefix, 'nuage_domain_create')
    expect_event(listener, name_prefix, 'nuage_zone_create')
    expect_event(listener, name_prefix, 'nuage_subnet_create')
    expect_event(listener, name_prefix, 'nuage_vport_create', comment='L3 cont')
    expect_event(listener, name_prefix, 'nuage_vport_create', comment='L3 vm')
    expect_event(listener, name_prefix, 'nuage_l2domaintemplate_create')
    expect_event(listener, name_prefix, 'nuage_l2domain_create')
    expect_event(listener, name_prefix, 'nuage_vport_create', comment='L2 cont')
    expect_event(listener, name_prefix, 'nuage_vport_create', comment='L2 vm')
    expect_event(listener, name_prefix, 'nuage_policygroup_create', comment='L1')
    expect_event(listener, name_prefix, 'nuage_policygroup_create', comment='L2')

    nuage = networks_provider.mgmt
    sandbox = create_basic_sandbox(nuage, prefix=name_prefix)

    enterprise = sandbox.enterprise['obj']
    nuage.delete_enterprise(enterprise)
    logger.info('Destroyed sandbox enterprise %s (%s)', enterprise.name, enterprise.id)


def test_creating_entities_triggers_targeted_refresh(targeted_refresh, with_nuage_sandbox):
    """
    Test whether targeted refresh is triggered when entities are created. This way
    we check whether Automation Instances are properly set to trigger targeted refresh
    when event comes.

    config:
        Before running this test you have to configure merkyl (see how in
        cfme/fixtures/merkyl.py) and make sure you have port 8192 opened
        on your appliance.

    Steps:
        * Deploy entities outside of CFME (directly in the provider)
        * Verify that targeted refreshes where triggered

    Important: targeted_refresh fixture must be listed before with_nuage_sandbox
    fixture because we have to start tracking evm.log before we create the entites

    Polarion:
        assignee: rhcf3_machine
        initialEstimate: 1/4h
    """
    sandbox = with_nuage_sandbox
    with targeted_refresh.timeout():
        targeted_refresh.register_target(sandbox.enterprise['id'], 'Enterprise')
        targeted_refresh.register_target(sandbox.domain['id'], 'Domain')
        targeted_refresh.register_target(sandbox.subnet['id'], 'Subnet')
        targeted_refresh.register_target(sandbox.cont_vport['id'], 'Container vPort (L3)')
        targeted_refresh.register_target(sandbox.vm_vport['id'], 'VM vPort (L3)')
        targeted_refresh.register_target(sandbox.l2_domain['id'], 'Domain (L2)')
        targeted_refresh.register_target(sandbox.l2_cont_vport['id'], 'Container vPort (L2)')
        targeted_refresh.register_target(sandbox.l2_vm_vport['id'], 'VM vPort (L2)')
        targeted_refresh.register_target(sandbox.group['id'], 'Security group (L3)')
        targeted_refresh.register_target(sandbox.l2_group['id'], 'Security group (L2)')


def expect_event(listener, name_prefix, event_type, comment=''):
    """
    Raise error unless event of type event_type is found with matching entity_id.

    Args:
        listener: instance of RestEventListener
        event_type: expected event type, e.g. 'nuage_subnet_create'
        entity_id: expected entity id, e.g. '184c55c9-5857-4404-bdcb-1ed99ec777eb'
        comment: comment that will be displayed if event was not emitted (optional)

    Returns: None
    """
    def cmp_function(_, full_data):
        # Nuage returns entities as a list, but there is always exactly one in there.
        return full_data['entities'][0]['name'].startswith(name_prefix)

    listener(
        {
            'full_data': '{} [NAME_PREFIX={}] {}'.format(event_type, name_prefix, comment),
            'cmp_func': cmp_function
        },
        source='NUAGE',
        event_type=event_type,
        first_event=True
    )
