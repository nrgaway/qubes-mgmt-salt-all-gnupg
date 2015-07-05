%{!?version: %define version %(cat version)}
%{!?rel: %define rel %(cat rel)}
%{!?formula_name: %define formula_name %(cat formula_name)}

Name:      qubes-mgmt-salt-base-gpg
Version:   %{version}
Release:   %{rel}%{?dist}
Summary:   Description: Custom gpg state, module and renderer
License:   GPL 2.0
URL:	   http://www.qubes-os.org/

Group:     System administration tools
BuildArch: noarch
Requires:  qubes-mgmt-salt-config

%define _builddir %(pwd)

%description
The custom state and module provides the ability to import or verify gpg keys,
while the custom renderer will fail to render a .sls state file if the state
file contains the #!verify shebang and the statefile fails verification do to
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
ln -sf /srv/formulas/base/gpg-formula/pillar/gnupg /srv/pillar/base/gnupg

%files
%defattr(-,root,root)
%attr(750, root, root) %dir /srv/formulas/base/%{formula_name}
/srv/formulas/base/%{formula_name}/*

%changelog
