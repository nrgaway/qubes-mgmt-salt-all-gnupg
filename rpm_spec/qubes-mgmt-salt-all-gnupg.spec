%{!?version: %define version %(make get-version)}
%{!?rel: %define rel %(make get-release)}
%{!?package_name: %define package_name %(make get-package_name)}
%{!?package_summary: %define package_summary %(make get-summary)}
%{!?package_description: %define package_description %(make get-description)}

%{!?formula_name: %define formula_name %(make get-formula_name)}
%{!?state_name: %define state_name %(make get-state_name)}
%{!?saltenv: %define saltenv %(make get-saltenv)}
%{!?pillar_dir: %define pillar_dir %(make get-pillar_dir)}
%{!?formula_dir: %define formula_dir %(make get-formula_dir)}

%{!?formula_root: %define formula_root %(make get-formula_root)}
%{!?testenv: %define testenv %(make get-testenv)}

Name:      %{package_name}
Version:   %{version}
Release:   %{rel}%{?dist}
Summary:   %{package_summary}
License:   GPL 2.0
URL:	   http://www.qubes-os.org/

Group:     System administration tools
BuildArch: noarch
Requires:  qubes-mgmt-salt
Requires:  qubes-mgmt-salt-all-yamlscript-renderer
Requires:  python-gnupg

%define _builddir %(pwd)

%description
%{package_description}

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
qubesctl topd.enable %{state_name} saltenv=%{saltenv} -l quiet --out quiet > /dev/null || true

# Enable Pillar States
qubesctl topd.enable %{state_name} saltenv=%{saltenv} pillar=true -l quiet --out quiet > /dev/null || true

# Enable Test States
#qubesctl topd.enable %{state_name}.test-gpg-renderer saltenv=%{testenv} -l quiet --out quiet > /dev/null || true
#qubesctl topd.enable %{state_name}.tests saltenv=%{testenv} -l quiet --out quiet > /dev/null || true

%files
%defattr(-,root,root)
%attr(750, root, root) %dir /srv/formulas/base/gnupg-formula
%attr(750, root, root) %dir /srv/formulas/base/gnupg-formula/gnupg
%attr(750, root, root) %dir /srv/formulas/base/gnupg-formula/_modules
%attr(750, root, root) %dir /srv/formulas/base/gnupg-formula/pillar
%attr(750, root, root) %dir /srv/formulas/base/gnupg-formula/_renderers
%attr(750, root, root) %dir /srv/formulas/base/gnupg-formula/pillar/gnupg
%attr(750, root, root) %dir /srv/formulas/base/gnupg-formula/pillar/gnupg/keys
%attr(750, root, root) %dir /srv/formulas/base/gnupg-formula/_states
/srv/formulas/base/gnupg-formula/gnupg/init.sls
/srv/formulas/base/gnupg-formula/gnupg/init.top
/srv/formulas/base/gnupg-formula/_modules/gnupg.py*
/srv/formulas/base/gnupg-formula/pillar/gnupg/init.sls
/srv/formulas/base/gnupg-formula/pillar/gnupg/init.top
/srv/formulas/base/gnupg-formula/pillar/gnupg/keys/nrgaway-qubes-signing-key.asc
/srv/formulas/base/gnupg-formula/_renderers/verify.py*
/srv/formulas/base/gnupg-formula/_states/gnupg.py*
/srv/formulas/base/gnupg-formula/README.rst
/srv/formulas/base/gnupg-formula/LICENSE

%attr(750, root, root) %dir /srv/formulas/test/gnupg-formula
%attr(750, root, root) %dir /srv/formulas/test/gnupg-formula/gnupg
/srv/formulas/test/gnupg-formula/LICENSE
/srv/formulas/test/gnupg-formula/README.rst
/srv/formulas/test/gnupg-formula/gnupg/test-gpg-renderer.sls
/srv/formulas/test/gnupg-formula/gnupg/test-gpg-renderer.sls.asc
/srv/formulas/test/gnupg-formula/gnupg/tests.sls

%attr(750, root, root) %dir /srv/pillar/base/gnupg
%config(noreplace) /srv/pillar/base/gnupg/init.sls
/srv/pillar/base/gnupg/init.top
/srv/pillar/base/gnupg/keys/nrgaway-qubes-signing-key.asc

%changelog
