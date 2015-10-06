#!yamlscript
# -*- coding: utf-8 -*-
# vim: set syntax=yaml ts=2 sw=2 sts=2 et :

##
# gnupg.tests
# ===========
#
# gpg module and renderer tests
#
# Execute:
#   qubesctl state.sls gnupg.tests
##


$python: |
    tests = [
        'debug-mode',
        'gnupg-import_key',
        'gnupg-verify',
        'gnupg-renderer',
    ]

#===============================================================================
# Set salt state result debug mode (enable/disable)                   debug-mode
#===============================================================================
$if 'debug-mode' in tests:
  gnupg-test-debug-mode-id:
    debug.mode:
      - enable-all: true
      # enable: [qvm.absent, qvm.start]
      # disable: [qvm.absent]
      # disable-all: true

#===============================================================================
# Test new state and module to import gpg key                   gnupg-import_key
#
# (moved to salt/gnupg.sls)
#===============================================================================
$if 'gnupg-import_key' in tests:
  gnupg-import_key-id:
    gnupg.import_key:
      # source: /srv/pillar/base/gnupg/keys/nrgaway-qubes-signing-key.asc
      - source: pillar://gnupg/keys/nrgaway-qubes-signing-key.asc
      # contents-pillar: gnupg-nrgaway-key
      # user: salt

#===============================================================================
# Test new state and module to verify detached signed file          gnupg-verify
#===============================================================================
$if 'gnupg-verify' in tests:
  gnupg-verify-id:
    gnupg.verify:
      # source: salt://gnupg/test-gpg-renderer.sls.asc@dom0
      - source: salt://gnupg/test-gpg-renderer.sls.asc
      # key-data: salt://gnupg/test-gpg-renderer.sls@dom0
      # user: salt
      # require:
      # - pkg: gnupg

#===============================================================================
# Test gpgrenderer that automatically verifies signed state       gnupg-renderer
# state files (vim/init.sls{.asc} is the test file for this)
#===============================================================================
$if 'gnupg-renderer' in tests:
  $include: gnupg.test-gpg-renderer
