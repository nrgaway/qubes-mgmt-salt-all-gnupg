# -*- coding: utf-8 -*-
#
# vim: set ts=4 sw=4 sts=4 et :
'''
:maintainer:    Jason Mehring <nrgaway@gmail.com>
:maturity:      new
:depends:       python-gpg
:platform:      all

Implementation of gpg utilities
===============================

.. code-block:: yaml

    vim.sls.asc:
      gnupg.verify
        - source: salt://vim/init.sls.asc
'''

# Import python libs
from __future__ import absolute_import
import logging

# Import salt libs
from salt.exceptions import (CommandExecutionError, SaltInvocationError)

# Import custom libs
from qubes_utils import Status  # pylint: disable=F0401

log = logging.getLogger(__name__)

__virtualname__ = 'gnupg'


def __virtual__():
    '''
    Return virtual name if gnupg module is also available.
    '''
    if 'gnupg.import_key' in __salt__:
        return __virtualname__
    return False


def _state_action(_action, *varargs, **kwargs):
    '''
    State helper function to call requested salt modules.
    '''
    try:
        status = __salt__[_action](*varargs, **kwargs)
    except (SaltInvocationError, CommandExecutionError) as err:
        status = Status(retcode=1, result=False, comment=err.message + '\n')
    return vars(status)


def import_key(*varargs, **kwargs):
    '''
    Import a gpg key.

    Gpg keys are imported into Salt's configuration directory usually located in
    `/etc/salt/gpgkeys` which are then used to verify signed state files.
    '''
    return _state_action('gnupg.import_key', *varargs, **kwargs)


def verify(*varargs, **kwargs):
    '''
    Verify a gpg key.
    '''
    return _state_action('gnupg.verify', *varargs, **kwargs)
