# -*- coding: utf-8 -*-
# vim: set syntax=yaml ts=2 sw=2 sts=2 et :

##
# tests - gnupg
# =============
#
# gpg module and renderer tests
#
# Execute:
#   qubesctl state.sls gnupg test
##

{% set tests = [
        'debug-mode',
        'gnupg-import_key',
        'gnupg-verify',
        'gnupg-renderer',
    ]
%}

#===============================================================================
# Set salt state result debug mode (enable/disable)                   debug-mode
#===============================================================================
{% if 'debug-mode' in tests %}
gnupg-test-debug-mode-id:
  debug.mode:
    - enable-all: true
{% endif %}

#===============================================================================
# Test new state and module to import gpg key                   gnupg-import_key
#
# (moved to salt/gnupg.sls)
#===============================================================================
{% if 'gnupg-import_key' in tests %}
gnupg-import_key-id:
  gnupg.import_key:
    - source: pillar://gnupg/keys/nrgaway-qubes-signing-key.asc
    # contents-pillar: gnupg-nrgaway-key
    # user: salt
{% endif %}

#===============================================================================
# Test new state and module to verify detached signed file          gnupg-verify
#===============================================================================
{% if 'gnupg-verify' in tests %}
gnupg-verify-id:
  gnupg.verify:
    - source: salt://gnupg/renderer.sls.asc?saltenv=test
    # data-source: salt://gnupg/renderer.sls?saltenv=test
    # user: salt
    # require:
    #   - pkg: gnupg
{% endif %}

#===============================================================================
# Test gnupg-renderer that automatically verifies signed state    gnupg-renderer
# state files (gnupg/renderer.sls{.asc} is the test file for this)
#===============================================================================
{% if 'gnupg-renderer' in tests %}
include:
  - gnupg.renderer
{% endif %}
