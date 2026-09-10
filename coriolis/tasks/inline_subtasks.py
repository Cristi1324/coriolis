# Copyright 2026 Cloudbase Solutions Srl
# All Rights Reserved.

"""Inline child tasks that run inside a parent worker process."""

import contextlib

from oslo_log import log as logging

from coriolis import constants, events

LOG = logging.getLogger(__name__)

_FINAL_STATUSES = (
    constants.TASK_STATUS_COMPLETED,
    constants.TASK_STATUS_ERROR,
    constants.TASK_STATUS_CANCELED,
    constants.TASK_STATUS_FORCE_CANCELED,
)


class InlineSubtaskSession(object):
    """Declare steps in memory. Create a DB row only when a step starts."""

    def __init__(self, event_handler, event_manager=None):
        self._root_handler = event_handler
        self._event_manager = event_manager or events.EventManager(event_handler)
        self._event_manager.inline_session = self
        self._specs = {}
        self._child_ids = {}
        self._statuses = {}

    @property
    def event_manager(self):
        return self._event_manager

    def define(self, specs):
        self._specs = {spec["id"]: dict(spec) for spec in specs}

    def _task_type(self, step_id):
        spec = self._specs.get(step_id) or {}
        return spec.get("task_type") or step_id

    def _dep_uuids(self, step_id):
        spec = self._specs.get(step_id) or {}
        ids = []
        for dep in spec.get("depends_on") or []:
            child_id = self._child_ids.get(dep)
            if child_id:
                ids.append(child_id)
        return ids

    def _result_id(self, result):
        if not result:
            return None
        if isinstance(result, dict):
            return result.get("id")
        return getattr(result, "id", None) or result

    def start(self, step_id):
        if step_id in self._child_ids:
            return self._child_ids[step_id]
        result = self._root_handler.create_inline_task(
            self._task_type(step_id), depends_on=self._dep_uuids(step_id)
        )
        task_id = self._result_id(result) or step_id
        self._child_ids[step_id] = task_id
        self._statuses[step_id] = constants.TASK_STATUS_RUNNING
        return task_id

    def _child_handler(self, task_id):
        for_subtask = getattr(self._root_handler, "for_subtask", None)
        if not for_subtask:
            return self._root_handler
        return for_subtask(task_id)

    @contextlib.contextmanager
    def target(self, step_id):
        task_id = self.start(step_id)
        previous = self._event_manager._event_handler
        self._event_manager._event_handler = self._child_handler(task_id)
        try:
            yield task_id
        finally:
            self._event_manager._event_handler = previous

    @contextlib.contextmanager
    def step(self, step_id):
        with self.target(step_id):
            try:
                yield self._child_ids[step_id]
            except Exception as ex:
                self.fail(step_id, ex)
                raise
            else:
                self.complete(step_id)

    def _set_status(self, step_id, status, exception_details=None):
        if step_id not in self._child_ids:
            return
        if self._statuses.get(step_id) in _FINAL_STATUSES:
            return
        setter = getattr(self._root_handler, "set_inline_task_status", None)
        if setter:
            setter(
                self._child_ids[step_id],
                status,
                exception_details=exception_details,
            )
        self._statuses[step_id] = status

    def complete(self, step_id):
        self._set_status(step_id, constants.TASK_STATUS_COMPLETED)

    def fail(self, step_id, exc):
        details = exc
        if not isinstance(exc, str):
            details = str(exc)
        self._set_status(
            step_id, constants.TASK_STATUS_ERROR, exception_details=details
        )

    def cancel(self, step_id):
        self._set_status(step_id, constants.TASK_STATUS_CANCELED)

    def fail_if_running(self, step_id, exc):
        if self._statuses.get(step_id) == constants.TASK_STATUS_RUNNING:
            self.fail(step_id, exc)
