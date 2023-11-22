# Copyright 2023 Cloudbase Solutions Srl
# All Rights Reserved.

from unittest import mock

from coriolis.api.v1 import endpoint_destination_minion_pool_options \
    as endpoint
from coriolis.api.v1.views import endpoint_options_view
from coriolis.endpoint_options import api
from coriolis.tests import test_base
from coriolis import utils


class EndpointDestinationMinionPoolOptionsControllerTestCase(
    test_base.CoriolisBaseTestCase
):
    "Test suite for the Coriolis api v1."""

    def setUp(self):
        super(
            EndpointDestinationMinionPoolOptionsControllerTestCase,
            self
        ).setUp()
        self.minion_api = \
            endpoint.EndpointDestinationMinionPoolOptionsController()

    @mock.patch('coriolis.policies.endpoints.ENDPOINTS_POLICY_PREFIX',
                'mock_prefix')
    @mock.patch.object(utils, 'decode_base64_param')
    @mock.patch.object(endpoint_options_view,
                       'destination_minion_pool_options_collection')
    @mock.patch.object(api.API,
                       'get_endpoint_destination_minion_pool_options')
    def test_index(
        self,
        mock_get_endpoint_destination_minion_pool_options,
        mock_destination_minion_pool_options_collection,
        mock_get_diagnostics_policy_label,
    ):
        mock_req = mock.Mock()
        mock_context = mock.Mock()
        endpoint_id = mock.sentinel.endpoint_id
        mock_req.environ = {'coriolis.context': mock_context}
        env = mock.sentinel.env
        options = mock.sentinel.options
        mock_req.GET = {
            'env': env,
            'options': options
        }

        expected_calls = [
            mock.call.mock_get_diagnostics_policy_label(
                env, is_json=True),
            mock.call.mock_get_diagnostics_policy_label(
                options, is_json=True)]

        result = self.minion_api.index(mock_req, endpoint_id)

        mock_get_diagnostics_policy_label.has_calls(expected_calls)
        (mock_get_endpoint_destination_minion_pool_options.
            assert_called_once_with)(
                mock_context, endpoint_id,
                env=mock_get_diagnostics_policy_label.return_value,
                option_names=mock_get_diagnostics_policy_label.return_value)
        (mock_destination_minion_pool_options_collection.
            assert_called_once_with)(
                mock_get_endpoint_destination_minion_pool_options.return_value)
        self.assertEqual(
            mock_destination_minion_pool_options_collection.return_value,
            result
        )

    @mock.patch('coriolis.policies.endpoints.ENDPOINTS_POLICY_PREFIX',
                'mock_prefix')
    @mock.patch.object(utils, 'decode_base64_param')
    @mock.patch.object(endpoint_options_view,
                       'destination_minion_pool_options_collection')
    @mock.patch.object(api.API,
                       'get_endpoint_destination_minion_pool_options')
    def test_index_no_env_and_options(
        self,
        mock_get_endpoint_destination_minion_pool_options,
        mock_destination_minion_pool_options_collection,
        mock_decode_base64_param,
    ):
        mock_req = mock.Mock()
        mock_context = mock.Mock()
        endpoint_id = mock.sentinel.endpoint_id
        mock_req.environ = {'coriolis.context': mock_context}
        mock_req.GET = {}

        result = self.minion_api.index(mock_req, endpoint_id)

        mock_decode_base64_param.assert_not_called()
        (mock_get_endpoint_destination_minion_pool_options.
            assert_called_once_with)(
                mock_context, endpoint_id,
                env={},
                option_names={})
        (mock_destination_minion_pool_options_collection.
            assert_called_once_with)(
                mock_get_endpoint_destination_minion_pool_options.return_value)
        self.assertEqual(
            mock_destination_minion_pool_options_collection.return_value,
            result
        )
