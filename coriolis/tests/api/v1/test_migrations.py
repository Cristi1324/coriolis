# Copyright 2023 Cloudbase Solutions Srl
# All Rights Reserved.

from unittest import mock

import ddt

from coriolis.api.v1 import migrations
from coriolis.api.v1 import utils as api_utils
from coriolis.api.v1.views import migration_view
from coriolis.migrations import api
from coriolis.policies import migrations as migration_policies
from coriolis.tests import test_base


@ddt.ddt
class MigrationControllerTestCase(
    test_base.CoriolisBaseTestCase
):
    "Test suite for the Coriolis api v1."""

    def setUp(self):
        super(MigrationControllerTestCase, self).setUp()
        self.migrations = migrations.MigrationController()

    @mock.patch.object(migration_view, 'single')
    @mock.patch.object(api.API, 'get_migration')
    @mock.patch.object(migration_policies, 'get_migrations_policy_label')
    @mock.patch('coriolis.api.v1.migrations.CONF')
    def test_show(
        self,
        mock_CONF,
        mock_get_migrations_policy_label,
        mock_get_migration,
        mock_single
    ):
        mock_req = mock.Mock()
        mock_context = mock.Mock()
        mock_req.environ = {'coriolis.context': mock_context}
        id = mock.sentinel.id
        mock_CONF.api.include_task_info_in_migrations_api = False

        result = self.migrations.show(mock_req, id)

        self.assertEqual(
            mock_single.return_value,
            result
        )

        mock_get_migrations_policy_label.assert_called_once_with("show")
        mock_get_migration.assert_called_once_with(
            mock_context, id, include_task_info=False
        )
        mock_single.assert_called_once_with(mock_get_migration.return_value)

    @ddt.data(
        (
            {
                "migration": {
                    "user_scripts": {"mock_user_scripts": None},
                    "instances": ["mock_instance1", "mock_instance2"],
                    "replica_id": "mock_replica_id",
                    "clone_disks": True,
                    "force": False,
                    "skip_os_morphing": False,
                    "instance_osmorphing_minion_pool_mappings":
                        {"mock_mapping": "mock_value"},
                }
            }
        ),
        (
            {
                "migration": {
                    "user_scripts": {"mock_user_scripts": None},
                    "instances": ["mock_instance1", "mock_instance2"],
                    "replica_id": None,
                    "clone_disks": True,
                    "force": False,
                    "skip_os_morphing": False,
                    "instance_osmorphing_minion_pool_mappings":
                        {"mock_mapping": "mock_value"},
                }
            }
        )
    )
    @mock.patch.object(migration_view, 'single')
    @mock.patch.object(api.API, 'migrate_instances')
    @mock.patch.object(migrations.MigrationController,
                       '_validate_migration_input')
    @mock.patch.object(api.API, 'deploy_replica_instances')
    @mock.patch.object(api_utils, 'normalize_user_scripts')
    @mock.patch.object(api_utils, 'validate_user_scripts')
    @mock.patch.object(migration_policies, 'get_migrations_policy_label')
    def test_create(
        self,
        data,
        mock_get_migrations_policy_label,
        mock_validate_user_scripts,
        mock_normalize_user_scripts,
        mock_deploy_replica_instances,
        mock__validate_migration_input,
        mock_migrate_instances,
        mock_single
    ):
        mock_req = mock.Mock()
        mock_context = mock.Mock()
        mock_req.environ = {'coriolis.context': mock_context}
        mock_values = [(f'mock_value_{i}') for i in range(1, 15)]
        mock__validate_migration_input.return_value = mock_values

        result = self.migrations.create(mock_req, data)

        self.assertEqual(
            mock_single.return_value,
            result
        )

        if data['migration']['replica_id'] is not None:
            mock_deploy_replica_instances.assert_called_with(
                mock_context,
                data['migration']['replica_id'],
                data['migration']['instance_osmorphing_minion_pool_mappings'],
                data['migration']['clone_disks'],
                data['migration']['force'],
                data['migration']['skip_os_morphing'],
                user_scripts=mock_normalize_user_scripts.return_value
            )
        else:
            mock__validate_migration_input.assert_called_with(
                mock_context,
                data
            )
            mock_migrate_instances.assert_called_with(
                mock_context, *mock_values[:8], *mock_values[12:],
                *mock_values[10:12],
                notes=mock_values[8],
                skip_os_morphing=mock_values[9],
                user_scripts=mock_normalize_user_scripts.return_value
            )
