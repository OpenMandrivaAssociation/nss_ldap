Summary:	NSS library and PAM module for LDAP
Name:		nss_ldap
Version:	265
Release:	8
License:	LGPLv2
Group:		System/Libraries
Url:		http://www.padl.com/
Source0:	http://www.padl.com/download/%{name}-%{version}.tar.gz
Patch0:		nss_ldap-265-Makefile.patch
Patch1:		nss_ldap-250-bind_policy_default_soft.patch
Patch2:		nss-ldap-automake-1.13.patch
BuildRequires:	openldap-devel
Suggests:	nscd

%description
This package includes two LDAP access clients:	nss_ldap and pam_ldap.
Nss_ldap is a set of C library extensions which allows X.500 and LDAP
directory servers to be used as a primary source of aliases, ethers,
groups, hosts, networks, protocol, users, RPCs, services and shadow
passwords (instead of or in addition to using flat files or NIS).

%prep
%setup -q
%apply_patches
# first line not commented upstream for some reason
perl -pi -e 's/^ /#/' ldap.conf
autoreconf

%build
%serverbuild
export CFLAGS="%{optflags} -fPIC"
%configure2_5x \
	--with-ldap-lib=openldap \
	--enable-rfc2307bis \
	--libdir=/%{_lib}
make INST_UID=`id -u` INST_GID=`id -g`

%install
install -d %{buildroot}%{_sysconfdir}
install -d %{buildroot}/%{_lib}/security

# Install the nsswitch module.
%make install DESTDIR="%{buildroot}" INST_UID=`id -u` INST_GID=`id -g` \
	libdir=/%{_lib}

echo "secret" > %{buildroot}/%{_sysconfdir}/ldap.secret

# Remove unpackaged file
rm -rf	%{buildroot}%{_sysconfdir}/nsswitch.ldap \
	%{buildroot}%{_libdir}/libnss_ldap.so.2

%post
if [ -f /etc/init.d/nscd ]; then
	/sbin/service nscd restart >/dev/null 2>/dev/null || :
fi

%postun
if [ -f /etc/init.d/nscd ]; then
	/sbin/service nscd restart >/dev/null 2>/dev/null || :
fi

%files
%doc ANNOUNCE AUTHORS ChangeLog COPYING NEWS README doc INSTALL
%doc nsswitch.ldap certutil ldap.conf
%attr (600,root,root) %config(noreplace) %{_sysconfdir}/ldap.secret
%attr (644,root,root) %config(noreplace) %{_sysconfdir}/ldap.conf
/%{_lib}/*so*
%{_mandir}/man5/nss_ldap.5.*

