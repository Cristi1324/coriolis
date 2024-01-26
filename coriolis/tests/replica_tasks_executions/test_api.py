# Copyright 2024 Cloudbase Solutions Srl
# All Rights Reserved.

from unittest import mock

from coriolis.replica_tasks_executions import api as replicas_module
from coriolis.tests import test_base


class APITestCase(test_base.CoriolisBaseTestCase):
    """Test suite for the Coriolis API class."""

    def setUp(self):
        super(APITestCase, self).setUp()
        self.api = replicas_module.API()
        self.rpc_client = mock.MagicMock()
        self.api._rpc_client = self.rpc_client
        self.ctxt = mock.sentinel.ctxt
        self.replica_id = mock.sentinel.replica_id
        self.execution_id = mock.sentinel.execution_id

    def test_create(self):
        shutdown_instances = mock.sentinel.shutdown_instances

        result = self.api.create(self.ctxt, self.replica_id,
                                 shutdown_instances)

        self.rpc_client.execute_replica_tasks.assert_called_once_with(
            self.ctxt, self.replica_id, shutdown_instances)
        self.assertEqual(result,
                         self.rpc_client.execute_replica_tasks.return_value)

    def test_delete(self):
        self.api.delete(self.ctxt, self.replica_id, self.execution_id)

        self.rpc_client.delete_replica_tasks_execution.assert_called_once_with(
            self.ctxt, self.replica_id, self.execution_id)

    def test_cancel(self):
        force = mock.sentinel.force

        self.api.cancel(self.ctxt, self.replica_id, self.execution_id, force)

        self.rpc_client.cancel_replica_tasks_execution.assert_called_once_with(
            self.ctxt, self.replica_id, self.execution_id, force)

    def test_get_executions(self):
        include_tasks = mock.sentinel.include_tasks

        result = self.api.get_executions(self.ctxt, self.replica_id,
                                         include_tasks)

        self.rpc_client.get_replica_tasks_executions.assert_called_once_with(
            self.ctxt, self.replica_id, include_tasks)
        self.assertEqual(
            result, self.rpc_client.get_replica_tasks_executions.return_value)

    def test_get_execution(self):
        result = self.api.get_execution(self.ctxt, self.replica_id,
                                        self.execution_id)

        self.rpc_client.get_replica_tasks_execution.assert_called_once_with(
            self.ctxt, self.replica_id, self.execution_id)
        self.assertEqual(
            result, self.rpc_client.get_replica_tasks_execution.return_value)
