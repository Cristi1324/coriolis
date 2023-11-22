# Copyright 2023 Cloudbase Solutions Srl
# All Rights Reserved.

from unittest import mock

from coriolis.api.v1 import endpoint_source_options as endpoint
from coriolis.api.v1.views import endpoint_options_view
from coriolis.endpoint_options import api
from coriolis.tests import test_base
from coriolis import utils


class EndpointSourceOptionsControllerTestCase(
    test_base.CoriolisBaseTestCase
):
    "Test suite for the Coriolis api v1."""

    def setUp(self):
        super(
            EndpointSourceOptionsControllerTestCase,
            self
        ).setUp()
        self.endpoint_api = \
            endpoint.EndpointSourceOptionsController()

    @mock.patch('coriolis.policies.endpoints.ENDPOINTS_POLICY_PREFIX',
                'mock_prefix')
    @mock.patch.object(utils, 'decode_base64_param')
    @mock.patch.object(endpoint_options_view, 'source_options_collection')
    @mock.patch.object(api.API, 'get_endpoint_source_options')
    def test_index(
        self,
        mock_get_endpoint_source_options,
        mock_source_options_collection,
        mock_decode_base64_param,
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
            mock.call.mock_decode_base64_param(
                env, is_json=True),
            mock.call.mock_decode_base64_param(
                options, is_json=True)]

        result = self.endpoint_api.index(mock_req, endpoint_id)

        mock_decode_base64_param.has_calls(expected_calls)
        (mock_get_endpoint_source_options.
            assert_called_once_with)(
                mock_context, endpoint_id,
                env=mock_decode_base64_param.return_value,
                option_names=mock_decode_base64_param.return_value)
        (mock_source_options_collection.
            assert_called_once_with)(
                mock_get_endpoint_source_options.return_value)
        self.assertEqual(
            mock_source_options_collection.return_value,
            result
        )

    @mock.patch('coriolis.policies.endpoints.ENDPOINTS_POLICY_PREFIX',
                'mock_prefix')
    @mock.patch.object(utils, 'decode_base64_param')
    @mock.patch.object(endpoint_options_view, 'source_options_collection')
    @mock.patch.object(api.API, 'get_endpoint_source_options')
    def test_index_no_env(
        self,
        mock_get_endpoint_source_options,
        mock_source_options_collection,
        mock_decode_base64_param,
    ):
        mock_req = mock.Mock()
        mock_context = mock.Mock()
        endpoint_id = mock.sentinel.endpoint_id
        mock_req.environ = {'coriolis.context': mock_context}
        mock_req.GET = {}

        result = self.endpoint_api.index(mock_req, endpoint_id)

        mock_decode_base64_param.assert_not_called()
        (mock_get_endpoint_source_options.
            assert_called_once_with)(
                mock_context, endpoint_id,
                env={},
                option_names={})
        (mock_source_options_collection.
            assert_called_once_with)(
                mock_get_endpoint_source_options.return_value)
        self.assertEqual(
            mock_source_options_collection.return_value,
            result
        )
