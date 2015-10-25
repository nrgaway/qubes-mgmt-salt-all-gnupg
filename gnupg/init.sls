# -*- coding: utf-8 -*-
# vim: set syntax=yaml ts=2 sw=2 sts=2 et :

##
# gnupg
# =====
#
# 1. Installs python-gnupg
# 2. Imports initial developer key(s)
#
# Execute:
#   qubesctl state.sls gnupg
##

gnupg:
  pkg.installed:
    - order: 1
    - names:
      - python-gnupg

  gnupg.import_key:
    - order: 1
    - source: pillar://gnupg/keys/nrgaway-qubes-signing-key.asc
    # contents-pillar: gnupg-nrgaway-key
