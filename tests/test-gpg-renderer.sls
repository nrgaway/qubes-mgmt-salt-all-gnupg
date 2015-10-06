#!verify|jinja|yaml
# -*- coding: utf-8 -*-
# vim: set syntax=yaml ts=2 sw=2 sts=2 et :

##
# gnupg.test-gpg-renderer
# =======================
#
# Execute:
#   qubesctl state.sls gnupg.test-gpg-renderer
##

gpg-renderer-test:
  pkg.installed:
    - names:
      - python-gnupg
