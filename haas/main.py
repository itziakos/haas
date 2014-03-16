# -*- coding: utf-8 -*-
# Copyright (c) 2013-2014 Simon Jagoe
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the 3-clause BSD license.  See the LICENSE.txt file for details.
from __future__ import absolute_import, unicode_literals  # pragma: no cover

import sys  # pragma: no cover

from .haas_application import HaasApplication  # pragma: no cover


def main():  # pragma: no cover
    """Execute haas.

    Parameters
    ----------
    argv : list
        The script's full argument list including the script itself.

    """
    application = HaasApplication(sys.argv)
    return application.run()
