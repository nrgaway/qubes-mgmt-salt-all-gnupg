#!verify|jinja|yaml
# -*- coding: utf-8 -*-
# vim: set syntax=yaml ts=2 sw=2 sts=2 et :

##
# tests - gnupg.renderer
# ======================
#
# The verify renderer will verify state/pillar file before rendering and prevent
# the file from being rendered if verification fails.  To manually create a
# matching gpg signature, sign a state / pillar as follows:
#
#   gpg --armor --detach-sig init.sls
#   gpg --import --homedir /etc/salt/gpgkeys nrgaway-qubes-signing-key.asc
#
# Execute:
#   qubesctl state.sls gnupg.renderer test
##

gnupg-renderer-test:
  pkg.installed:
    - names:
      - python-gnupg
