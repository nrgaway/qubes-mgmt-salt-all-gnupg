# -*- coding: utf-8 -*-
#
# vim: set ts=4 sw=4 sts=4 et :
'''
:maintainer:    Jason Mehring <nrgaway@gmail.com>
:maturity:      new
:depends:       python-gpg
:platform:      all

Renderer that verifies state and pillar files
=============================================

This renderer requires the python-gnupg package. Be careful to install the
``python-gnupg`` package, not the ``gnupg`` package, or you will get errors.

To set things up, you will first need to generate import a public key.  On
your master, run:

.. code-block:: bash

    $ gpg --import --homedir /etc/salt/gpgkeys pubkey.gpg

.. code-block:: yaml

    renderer: verify | jinja | yaml
'''

# Import python libs
from __future__ import absolute_import
import logging

# Import salt libs
import salt.utils
from salt.exceptions import (SaltRenderError, CommandExecutionError)

# Import third party libs
try:
    import gnupg  # pylint: disable=W0611
    HAS_GPG = True
    if salt.utils.which('gpg') is None:
        HAS_GPG = False
except ImportError:
    HAS_GPG = False

log = logging.getLogger(__name__)

# Define the module's virtual name
__virtualname__ = 'verify'


def __virtual__():
    '''
    Confine this module to gpg enabled systems.
    '''
    if HAS_GPG:
        return __virtualname__
    return False


def render(data, saltenv='base', sls='', argline='', **kwargs):  # pylint: disable=W0613
    '''
    Verify state or pillar file using detached signature file.

    Use the same name as state/pillar file with the additional '.asc' suffix.
    '''
    # Verify signed file
    try:
        client = salt.fileclient.get_file_client(__opts__)
        state = client.get_state(sls, saltenv)
        signature_file = client.cache_file(state['source'] + '.asc', saltenv)
        __salt__['gnupg.verify'](signature_file)
        return data

    except CommandExecutionError as error:
        raise SaltRenderError('GPG validation failed: {0}'.format(error))
