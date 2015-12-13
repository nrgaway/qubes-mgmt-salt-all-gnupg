%{!?version: %define version %(cat version)}

Name:      qubes-mgmt-salt-all-gnupg
Version:   %{version}
Release:   1%{?dist}
Summary:   Custom gpg state, module and renderer
License:   GPL 2.0
URL:	   http://www.qubes-os.org/

Group:     System administration tools
BuildArch: noarch
Requires:  qubes-mgmt-salt
Requires:  qubes-mgmt-salt-all-yamlscript-renderer
Requires:  python-gnupg

%define _builddir %(pwd)

%description
The custom state and module provides the ability to import or verify gpg keys,
while the custom renderer will fail to render a .sls state file if the state
file contains the \#!verify shebang and the statefile fails verification do to
any reason such as missing key, missing detached signature.

%prep
# we operate on the current directory, so no need to unpack anything
# symlink is to generate useful debuginfo packages
rm -f %{name}-%{version}
ln -sf . %{name}-%{version}
%setup -T -D

%build

%install
make install DESTDIR=%{buildroot} LIBDIR=%{_libdir} BINDIR=%{_bindir} SBINDIR=%{_sbindir} SYSCONFDIR=%{_sysconfdir}

%post
# Update Salt Configuration
qubesctl state.sls config -l quiet --out quiet > /dev/null || true
qubesctl saltutil.clear_cache -l quiet --out quiet > /dev/null || true
qubesctl saltutil.sync_all refresh=true -l quiet --out quiet > /dev/null || true

# Enable States
qubesctl top.enable gnupg saltenv=base -l quiet --out quiet > /dev/null || true

# Enable Pillar States
qubesctl top.enable gnupg saltenv=base pillar=true -l quiet --out quiet > /dev/null || true

# Enable Test States
#qubesctl top.enable gnupg saltenv=test -l quiet --out quiet > /dev/null || true
#qubesctl top.enable gnupg.renderer saltenv=test -l quiet --out quiet > /dev/null || true

%files
%defattr(-,root,root)
%doc LICENSE README.rst
%attr(750, root, root) %dir /srv/formulas/base/gnupg-formula
/srv/formulas/base/gnupg-formula/gnupg/init.sls
/srv/formulas/base/gnupg-formula/gnupg/init.top
/srv/formulas/base/gnupg-formula/_modules/ext_module_gnupg.py*
/srv/formulas/base/gnupg-formula/pillar/gnupg/init.sls
/srv/formulas/base/gnupg-formula/pillar/gnupg/init.top
/srv/formulas/base/gnupg-formula/pillar/gnupg/keys/nrgaway-qubes-signing-key.asc
/srv/formulas/base/gnupg-formula/_renderers/ext_renderer_verify.py*
/srv/formulas/base/gnupg-formula/_states/ext_state_gnupg.py*
/srv/formulas/base/gnupg-formula/README.rst
/srv/formulas/base/gnupg-formula/LICENSE

%attr(750, root, root) %dir /srv/formulas/test/gnupg-formula
/srv/formulas/test/gnupg-formula/LICENSE
/srv/formulas/test/gnupg-formula/README.rst
/srv/formulas/test/gnupg-formula/gnupg/init.sls
/srv/formulas/test/gnupg-formula/gnupg/renderer.sls
/srv/formulas/test/gnupg-formula/gnupg/renderer.sls.asc

%attr(750, root, root) %dir /srv/pillar/base/gnupg
%config(noreplace) /srv/pillar/base/gnupg/init.sls
/srv/pillar/base/gnupg/init.top
/srv/pillar/base/gnupg/keys/nrgaway-qubes-signing-key.asc

%changelog
