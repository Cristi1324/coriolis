# Copyright 2026 Cloudbase Solutions Srl
# All Rights Reserved.

from unittest import mock

from coriolis import constants
from coriolis.tasks import inline_subtasks
from coriolis.tests import test_base


class InlineSubtaskSessionTestCase(test_base.CoriolisBaseTestCase):
    def setUp(self):
        super(InlineSubtaskSessionTestCase, self).setUp()
        self.handler = mock.Mock()
        self.handler.create_inline_task.side_effect = (
            lambda task_type, depends_on=None: {"id": "id-%s" % task_type}
        )
        self.event_manager = mock.Mock()
        self.event_manager._event_handler = self.handler
        self.session = inline_subtasks.InlineSubtaskSession(
            self.handler, self.event_manager
        )
        self.session.define(
            [
                {"id": "pre_os_mount", "depends_on": []},
                {
                    "id": "download_virtio",
                    "depends_on": ["pre_os_mount"],
                    "optional": True,
                },
                {
                    "id": "configure_guest_no_resources",
                    "depends_on": ["pre_os_mount"],
                },
            ]
        )

    def test_define_does_not_create_rows(self):
        self.handler.create_inline_task.assert_not_called()

    def test_step_creates_row_and_completes(self):
        with self.session.step("pre_os_mount"):
            self.handler.create_inline_task.assert_called_once_with(
                "pre_os_mount", depends_on=[]
            )
        self.handler.set_inline_task_status.assert_called_once_with(
            "id-pre_os_mount",
            constants.TASK_STATUS_COMPLETED,
            exception_details=None,
        )

    def test_step_failure_sets_error(self):
        with self.assertRaises(ValueError):
            with self.session.step("pre_os_mount"):
                raise ValueError("boom")
        self.handler.set_inline_task_status.assert_called_once_with(
            "id-pre_os_mount",
            constants.TASK_STATUS_ERROR,
            exception_details="boom",
        )

    def test_depends_on_uses_created_sibling_uuids(self):
        self.session.start("pre_os_mount")
        self.session.complete("pre_os_mount")
        self.session.start("configure_guest_no_resources")
        self.handler.create_inline_task.assert_any_call(
            "configure_guest_no_resources", depends_on=["id-pre_os_mount"]
        )

    def test_skipped_dependency_is_omitted(self):
        self.session.start("configure_guest_no_resources")
        self.handler.create_inline_task.assert_called_once_with(
            "configure_guest_no_resources", depends_on=[]
        )

    def test_complete_is_noop_when_step_never_started(self):
        self.session.complete("download_virtio")
        self.handler.set_inline_task_status.assert_not_called()
