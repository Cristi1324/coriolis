# Copyright 2023 Cloudbase Solutions Srl
# All Rights Reserved.

from unittest import mock

from coriolis.api.v1 import migration_actions
from coriolis import exception
from coriolis.migrations import api
from coriolis.policies import migrations as migration_policies
from coriolis.tests import test_base

from webob import exc


class MigrationActionsControllerTestCase(
    test_base.CoriolisBaseTestCase
):
    "Test suite for the Coriolis api v1."""

    def setUp(self):
        super(MigrationActionsControllerTestCase, self).setUp()
        self.migration_actions = migration_actions.MigrationActionsController()

    @mock.patch.object(migration_policies, 'get_migrations_policy_label')
    @mock.patch.object(api.API, 'cancel')
    def test__cancel(
        self,
        mock_cancel,
        mock_get_migrations_policy_label,
    ):
        mock_req = mock.Mock()
        mock_context = mock.Mock()
        mock_req.environ = {'coriolis.context': mock_context}
        id = mock.sentinel.id
        mock_body = {
            'cancel': {
                'force': False
            }
        }

        self.assertRaises(
            exc.HTTPNoContent,
            self.migration_actions._cancel,
            mock_req,
            id,
            mock_body
        )

        mock_get_migrations_policy_label.assert_called_once_with("cancel")
        mock_cancel.assert_called_once_with(mock_context, id, False)

    @mock.patch.object(migration_policies, 'get_migrations_policy_label')
    @mock.patch.object(api.API, 'cancel')
    def test__cancel_empty(
        self,
        mock_cancel,
        mock_get_migrations_policy_label,
    ):
        mock_req = mock.Mock()
        mock_context = mock.Mock()
        mock_req.environ = {'coriolis.context': mock_context}
        id = mock.sentinel.id
        mock_body = {'cancel': {}}

        self.assertRaises(
            exc.HTTPNoContent,
            self.migration_actions._cancel,
            mock_req,
            id,
            mock_body
        )

        mock_get_migrations_policy_label.assert_called_once_with("cancel")
        mock_cancel.assert_called_once_with(mock_context, id, False)

    @mock.patch.object(migration_policies, 'get_migrations_policy_label')
    @mock.patch.object(api.API, 'cancel')
    def test__cancel_not_found(
        self,
        mock_cancel,
        mock_get_migrations_policy_label,
    ):
        mock_req = mock.Mock()
        mock_context = mock.Mock()
        mock_req.environ = {'coriolis.context': mock_context}
        id = mock.sentinel.id
        mock_body = {'cancel': {}}
        mock_cancel.side_effect = exception.NotFound()

        self.assertRaises(
            exc.HTTPNotFound,
            self.migration_actions._cancel,
            mock_req,
            id,
            mock_body
        )

        mock_get_migrations_policy_label.assert_called_once_with("cancel")
        mock_cancel.assert_called_once_with(mock_context, id, False)

    @mock.patch.object(migration_policies, 'get_migrations_policy_label')
    @mock.patch.object(api.API, 'cancel')
    def test__cancel_invalid_parameter_value(
        self,
        mock_cancel,
        mock_get_migrations_policy_label,
    ):
        mock_req = mock.Mock()
        mock_context = mock.Mock()
        mock_req.environ = {'coriolis.context': mock_context}
        id = mock.sentinel.id
        mock_body = {'cancel': {}}
        mock_cancel.side_effect = exception.InvalidParameterValue("err")

        self.assertRaises(
            exc.HTTPNotFound,
            self.migration_actions._cancel,
            mock_req,
            id,
            mock_body
        )

        mock_get_migrations_policy_label.assert_called_once_with("cancel")
        mock_cancel.assert_called_once_with(mock_context, id, False)
