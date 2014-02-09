# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import unicode_literals

import sys
from unittest.suite import _ErrorHolder


class _TestSuiteState(object):

    def __init__(self, result):
        self._result = result
        self._previous_class = None
        self._module_setup_failed = False
        self._class_setup_failed = False

    def _run_setup(self, item, setup_name, error_name):
        setup = getattr(item, setup_name, lambda: None)
        try:
            setup()
        except Exception:
            error = '{0} ({1})'.format(setup_name, error_name)
            # FIXME: _ErrorHolder
            self._result.addError(_ErrorHolder(error), sys.exc_info())
            return False
        return True

    def _setup_module(self, module_name):
        if self._previous_class is not None:
            previous_module = self._previous_class.__module__
            if previous_module == module_name:
                return
            self._teardown_module(previous_module)

        module = sys.modules.get(module_name)
        if module is None:
            return

        self._module_setup_failed = not self._run_setup(
            module, 'setUpModule', module_name)

    def _setup_class(self, current_class):
        previous_class = self._previous_class
        if previous_class == current_class:
            return
        if self._module_setup_failed:
            return
        if getattr(current_class, '__unittest_skip__', False):
            return

        self._class_setup_failed = not self._run_setup(
            current_class, 'setUpClass', current_class.__name__)
        self._previous_class = current_class

    def setup(self, test):
        current_class = test.__class__
        module = current_class.__module__
        self._teardown_previous_class(current_class)
        self._setup_module(module)
        self._setup_class(current_class)
        return not (self._class_setup_failed or self._module_setup_failed)

    def _teardown_previous_class(self, current_class):
        previous_class = self._previous_class
        if previous_class is None:
            return
        if current_class == self._previous_class:
            return
        if self._class_setup_failed:
            self._class_setup_failed = False
            return
        if self._module_setup_failed:
            return
        if getattr(previous_class, '__unittest_skip__', False):
            return

        self._run_setup(
            previous_class, 'tearDownClass', previous_class.__name__)

    def _teardown_module(self, module_name):
        if self._module_setup_failed:
            self._module_setup_failed = False
            return

        module = sys.modules[module_name]
        if module is None:
            return

        self._run_setup(module, 'tearDownModule', module_name)

    def teardown(self):
        if self._previous_class is None:
            return
        self._teardown_previous_class(None)
        previous_module = self._previous_class.__module__
        self._teardown_module(previous_module)


class TestSuite(object):

    def __init__(self, tests=()):
        self._tests = tuple(tests)

    def __iter__(self):
        return iter(self._tests)

    def __eq__(self, other):
        try:
            other_iter = iter(other)
        except TypeError:
            return NotImplemented
        return list(self) == list(other_iter)

    def __ne__(self, other):
        return not (self == other)

    def __call__(self, *args, **kwds):
        return self.run(*args, **kwds)

    def run(self, result):
        state = _TestSuiteState(result)
        for test in self:
            if state.setup(test):
                test(result)
        state.teardown()
        return result

    def countTestCases(self):
        return sum(test.countTestCases() for test in self)
