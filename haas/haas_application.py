# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import unicode_literals

import argparse
import os

from .discoverer import Discoverer
from .environment import Environment
from .loader import Loader
from .testing import unittest
from .utils import find_module_by_name


def parse_args(argv):
    """Parse command-line arguments.

    Parameters
    ----------
    argv : list
        The script's full argument list including the script itself.

    """
    parser = argparse.ArgumentParser(prog='haas')
    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument('-v', '--verbose', action='store_const', default=1,
                           dest='verbosity', const=2, help='Verbose output')
    verbosity.add_argument('-q', '--quiet', action='store_const', const=0,
                           dest='verbosity', help='Quiet output')
    parser.add_argument('-f', '--failfast', action='store_true', default=False,
                        help='Stop on first fail or error')
    parser.add_argument('-c', '--catch', dest='catch_interrupt',
                        action='store_true', default=False,
                        help=('(Ignored) Catch ctrl-C and display results so '
                              'far'))
    parser.add_argument('-b', '--buffer', action='store_true', default=False,
                        help='Buffer stdout and stderr during tests')
    parser.add_argument(
        'start', nargs='?', default=os.getcwd(),
        help=('Directory or dotted package/module name to start searching for '
              'tests'))
    parser.add_argument('-p', '--pattern', default='test*.py',
                        help="Pattern to match tests ('test*.py' default)")
    parser.add_argument('-t', '--top-level-directory', default=None,
                        help=('Top level directory of project (defaults to '
                              'start directory)'))
    parser.add_argument('-s', '--start-directory', action='store_const',
                        const=None,
                        help=('Ignored; use the start argument instead '
                              '(compatibility with unittest)'))
    parser.add_argument('--config', help='Ignored (reserved)')
    parser.add_argument('--environment-manager',
                        help='Class to use as the test environment manager')
    return parser.parse_known_args(argv[1:])


class HaasApplication(object):

    def __init__(self, argv, **kwargs):
        super(HaasApplication, self).__init__(**kwargs)
        self.argv = argv
        self.args, self.unparsed_args = parse_args(argv)

    def load_plugin_class(self, class_spec):
        if class_spec is None:
            return None
        try:
            module, module_attributes = find_module_by_name(class_spec)
        except ImportError:
            return None
        if len(module_attributes) != 1:
            return None
        klass = getattr(module, module_attributes[0], None)
        if klass is None:
            return None
        return [klass()]

    def run(self):
        args = self.args
        environment_plugin = self.load_plugin_class(
            args.environment_manager)
        with Environment(environment_plugin):
            loader = Loader()
            discoverer = Discoverer(loader)
            suite = discoverer.discover(
                start=args.start,
                top_level_directory=args.top_level_directory,
                pattern=args.pattern,
            )
            runner = unittest.TextTestRunner(
                verbosity=args.verbosity,
                failfast=args.failfast,
                buffer=args.buffer,
            )
            result = runner.run(suite)
            return not result.wasSuccessful()
