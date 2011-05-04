%define name 	nss_ldap
%define version 265
%define release %mkrel 4

Summary:	NSS library and PAM module for LDAP
Name: 		%{name}
Version: 	%{version}
Release: 	%{release}
License:	LGPL
Group:		System/Libraries
URL: 		http://www.padl.com/
BuildRequires:	openldap-devel >= 2.0.7-7.1mdk
BuildRequires:	automake
Source0:	http://www.padl.com/download/%{name}-%{version}.tar.gz
Patch0:		nss_ldap-265-Makefile.patch
Patch1:		nss_ldap-250-bind_policy_default_soft.patch
Suggests:	nscd
BuildRoot: 	%{_tmppath}/%{name}-%{version}-buildroot

%description
This package includes two LDAP access clients: nss_ldap and pam_ldap.
Nss_ldap is a set of C library extensions which allows X.500 and LDAP
directory servers to be used as a primary source of aliases, ethers,
groups, hosts, networks, protocol, users, RPCs, services and shadow
passwords (instead of or in addition to using flat files or NIS).

%prep
rm -rf %{buildroot}

%setup -q
%patch0 -p1 -b .makefile
%patch1 -p1 -b .bind_policy_soft
# first line not commented upstream for some reason
perl -pi -e 's/^ /#/' ldap.conf

%build

%serverbuild
autoreconf
%configure2_5x \
    --with-ldap-lib=openldap \
    --enable-rfc2307bis \
    --libdir=/%{_lib}
%__make INST_UID=`id -u` INST_GID=`id -g`

%install
rm -rf %{buildroot}

install -d %{buildroot}%{_sysconfdir}
install -d %{buildroot}/%{_lib}/security

# Install the nsswitch module.
%make install DESTDIR="${RPM_BUILD_ROOT}" INST_UID=`id -u` INST_GID=`id -g` \
	libdir=/%{_lib}

echo "secret" > %{buildroot}/%{_sysconfdir}/ldap.secret

# Remove unpackaged file
rm -rf	%{buildroot}%{_sysconfdir}/nsswitch.ldap \
	%{buildroot}%{_libdir}/libnss_ldap.so.2

%clean
rm -rf %{buildroot}

%post
%if %mdkversion < 200900
/sbin/ldconfig
%endif
if [ -f /etc/init.d/nscd ]; then
	/sbin/service nscd restart >/dev/null 2>/dev/null || :
fi

%postun
%if %mdkversion < 200900
/sbin/ldconfig
%endif
if [ -f /etc/init.d/nscd ]; then
	/sbin/service nscd restart >/dev/null 2>/dev/null || :
fi

%files
%defattr(-,root,root)
%doc ANNOUNCE AUTHORS ChangeLog COPYING NEWS README doc INSTALL
%doc nsswitch.ldap certutil ldap.conf
%attr (600,root,root) %config(noreplace) %{_sysconfdir}/ldap.secret
%attr (644,root,root) %config(noreplace) %{_sysconfdir}/ldap.conf
/%{_lib}/*so*
%{_mandir}/man5/nss_ldap.5.*


