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
'''

# pylint: disable=E1101,E1103

# Import python libs
from __future__ import absolute_import
import argparse  # pylint: disable=E0598
import logging
import os

# Import salt libs
import salt.modules.gpg as _gpg
import salt.utils
from salt.exceptions import (CommandExecutionError, SaltInvocationError)

# Import third party libs
try:
    import gnupg as _gnupg  # pylint: disable=W0611
    HAS_LIBS = True
except ImportError:
    HAS_LIBS = False

# Import custom libs
import module_utils  # pylint: disable=F0401
from module_utils import ModuleBase as _ModuleBase  # pylint: disable=F0401
from qubes_utils import Status  # pylint: disable=F0401
from qubes_utils import coerce_to_string as _coerce_to_string  # pylint: disable=F0401

# Set up logging
log = logging.getLogger(__name__)

# Define the module's virtual name
__virtualname__ = 'gnupg'


def __virtual__():
    '''
    Make sure that python-gnupg and gpg are available.
    '''
    if salt.utils.which('gpg') and HAS_LIBS:
        return __virtualname__
    return False


# pylint: disable=R0903
class _GPGBase(_ModuleBase):
    '''
    Overrides.
    '''

    # pylint: disable=E1002
    def __init__(self, __virtualname__, *varargs, **kwargs):
        '''
        '''
        if not hasattr(module_utils, '__opts__'):
            module_utils.__opts__ = __opts__
        if not hasattr(module_utils, '__salt__'):
            module_utils.__salt__ = __salt__

        super(_GPGBase, self).__init__(__virtualname__, *varargs, **kwargs)


def _get_path(filename, pillar=False):
    '''
    Attempt to convert filename to salt URL.
    '''
    if not filename:
        return ''

    saltenv = 'base'
    if filename.startswith('pillar://'):
        pillar = True
        filename = filename.replace('pillar://', 'salt://')

    if filename.startswith('salt://'):
        try:
            env_splitter = '?saltenv='
            filename, saltenv = filename.split(env_splitter)
        except ValueError:
            pass

    client = salt.fileclient.get_file_client(__opts__, pillar)
    if pillar:
        file_roots = client.opts['file_roots']
        client.opts['file_roots'] = client.opts['pillar_roots']

    filename = client.cache_file(filename, saltenv)
    if pillar:
        client.opts['file_roots'] = file_roots

    if not filename or not os.path.exists(filename):
        filename = ''
    return filename


def _get_data(filename):
    '''
    Attempt to read data from filesystem.
    '''
    try:
        with open(filename) as file_:
            return file_.read()
    except IOError as error:
        raise CommandExecutionError(
            'Error reading: {0}. {1}'.format(
                filename, error
            )
        )


def _import(user=None, text=None, filename=None):
    '''
    salt.module.gpg.import_key is broken, so implement it here for now.
    '''
    ret = {'result': False, 'message': 'Unable to import key.'}

    gnupg = _gpg._create_gpg(user)  # pylint: disable=W0212

    if not text and not filename:
        raise SaltInvocationError('filename or text must be passed.')

    if filename:
        try:
            with salt.utils.flopen(filename, 'rb') as _fp:
                lines = _fp.readlines()
                text = ''.join(lines)
        except IOError:
            raise SaltInvocationError('filename does not exist.')

    imported_data = gnupg.import_keys(text)
    log.debug('imported_data {0}'.format(imported_data.__dict__.keys()))
    log.debug('imported_data {0}'.format(imported_data.counts))

    results = imported_data.results[-1]
    if results.get('fingerprint', None) and 'ok' in results:
        ret['result'] = True

    ret['message'] = results.get('text', imported_data.summary())
    ret['stdout'] = imported_data.stderr
    return ret


def import_key(*varargs, **kwargs):
    '''
    Import a key from text or file.

    user
        Which user's keychain to access, defaults to user Salt is running as.
        Passing the user as 'salt' will set the GPG home directory to
        /etc/salt/gpgkeys.

    contents
        The text containing import key to import.

    contents-pillar
        The pillar id containing import key to import.

    source
        The filename containing the key to import.

    CLI Example:

    .. code-block:: bash

        qubesctl gnupg.import_key contents='-----BEGIN PGP PUBLIC KEY BLOCK-----
        ... -----END PGP PUBLIC KEY BLOCK-----'

        qubesctl gnupg.import_key source='/path/to/public-key-file'

        qubesctl gnupg.import_key contents-piller='gnupg:gpgkeys'
    '''
    base = _GPGBase('gpg.import_key', **kwargs)
    base.parser.add_argument('name', nargs='?', help=argparse.SUPPRESS)
    group = base.parser.add_mutually_exclusive_group()

    group.add_argument(
        'source',
        nargs='?',
        help='The filename containing the key to import'
    )

    group.add_argument(
        '--contents',
        nargs=1,
        metavar='TEXT',
        help='The text containing import key to import'
    )

    group.add_argument(
        '--contents-pillar',
        '--contents_pillar',
        type=_coerce_to_string,
        nargs=1,
        metavar='PILLAR-ID',
        help='The pillar id containing import key to import'
    )

    base.parser.add_argument(
        '--user',
        nargs=1,
        default='salt',
        help="Which user's keychain to access, defaults to user Salt is \
        running as.  Passing the user as 'salt' will set the GPG home \
        directory to /etc/salt/gpgkeys."
    )

    args = base.parse_args(*varargs, **kwargs)
    base.args.contents_pillar = _coerce_to_string(
        base.args.contents_pillar
    ) if base.args.contents_pillar else base.args.contents_pillar

    keywords = {'user': args.user, }
    status = Status()
    if args.source:
        keywords['filename'] = _get_path(args.source)
        if not keywords['filename']:
            status.recode = 1
            status.message = 'Invalid filename source {0}'.format(args.source)

    elif args.contents:
        keywords['text'] = args.contents

    elif args.contents_pillar:
        keywords['text'] = __pillar__.get(args.contents_pillar, None)
        if not keywords['text']:
            status.recode = 1
            status.message = 'Invalid pillar id source {0}'.format(
                args.contents_pillar
            )

    else:
        status.recode = 1
        status.message = 'Invalid options!'

    if status.failed():
        base.save_status(status)
    if __opts__['test']:
        base.save_status(message='Key will be imported')
    else:
        status = Status(**_import(**keywords))
        base.save_status(status)

    # Returns the status 'data' dictionary
    return base.status()


def verify(name, *varargs, **kwargs):
    '''
    Verify a message or file.

    source
        The filename.asc to verify.

    key-content
        The text to verify.

    data-source
        The filename data to verify.

    user
        Which user's keychain to access, defaults to user Salt is running as.
        Passing the user as 'salt' will set the GPG home directory to
        /etc/salt/gpgkeys.

    CLI Example:

    .. code-block:: bash

        qubesctl gnupg.verify source='/path/to/important.file.asc'

        qubesctl gnupg.verify <source|key-content> [key-data] [user=]

    '''
    base = _GPGBase('gpg.verify', **kwargs)
    base.parser.add_argument('name', help='The name id of state object')
    group = base.parser.add_mutually_exclusive_group()

    group.add_argument(
        'source',
        nargs='?',
        help='The filename containing the key to import'
    )

    group.add_argument(
        '--key-contents',
        '--key_contents',
        nargs=1,
        help='The text containing import key to import'
    )

    base.parser.add_argument(
        '--data-source',
        '--data_source',
        nargs='?',
        help='Source file data path to verify (source)'
    )

    base.parser.add_argument(
        '--user',
        nargs=1,
        default='salt',
        help="Which user's keychain to access, defaults to user Salt is \
        running as.  Passing the user as 'salt' will set the GPG home \
        directory to /etc/salt/gpgkeys."
    )

    args = base.parse_args(name, *varargs, **kwargs)
    gnupg = _gpg._create_gpg(args.user)  # pylint: disable=W0212
    status = Status()

    # Key source validation
    if args.source:
        key_source = _get_path(args.source)
        if not key_source:
            status.recode = 1
            status.message = 'GPG validation failed: invalid key-source {0}'.format(
                key_source
            )

    elif args.key_contents:
        key_source = args.key_contents

    else:
        key_source = _get_path(args.name)

    # Data source validation
    data_source = _get_path(args.data_source)
    if not data_source:
        data_source, ext = os.path.splitext(key_source)  # pylint: disable=W0612

    if not os.path.exists(data_source):
        status.retcode = 1
        message = 'GPG validation failed: invalid data-source {0}'.format(
            data_source
        )
        base.save_status(status, message=message)
        return base.status()

    # GPG verify
    status = Status()
    data = gnupg.verify_data(key_source, _get_data(data_source))

    if not data.valid:
        raise CommandExecutionError(data.stderr)

    status.stdout = data.stderr
    base.save_status(status)

    # Returns the status 'data' dictionary
    return base.status()
