%define name 	nss_ldap
%define version 259
%define release %mkrel 1

Summary:	NSS library and PAM module for LDAP
Name: 		%{name}
Version: 	%{version}
Release: 	%{release}
License:	LGPL
Group:		System/Libraries
URL: 		http://www.padl.com/
BuildRequires:	openldap-devel >= 2.0.7-7.1mdk
BuildRequires:	automake1.4
Source0:	http://www.padl.com/download/%{name}-%{version}.tar.gz
Patch0:		nss_ldap-makefile.patch
Patch1:		nss_ldap-250-bind_policy_default_soft.patch
BuildRoot: 	%{_tmppath}/%{name}-%{version}-buildroot

%description
This package includes two LDAP access clients: nss_ldap and pam_ldap.
Nss_ldap is a set of C library extensions which allows X.500 and LDAP
directory servers to be used as a primary source of aliases, ethers,
groups, hosts, networks, protocol, users, RPCs, services and shadow
passwords (instead of or in addition to using flat files or NIS).

%prep
rm -rf $RPM_BUILD_ROOT

%setup -q
%patch0 -p1 -b .makefile
%patch1 -p1 -b .bind_policy_soft
# first line not commented upstream for some reason
perl -pi -e 's/^ /#/' ldap.conf

%build

%serverbuild
# Build nss_ldap.
#aclocal && automake && autoheader && autoconf
#autoreconf --force

rm -f configure
libtoolize --copy --force; aclocal; autoconf; automake

%configure --enable-schema-mapping --with-ldap-lib=openldap --enable-debug \
--enable-rfc2307bis --enable-sfu-mapping --enable-ids-uid --libdir=/%{_lib}
%__make INST_UID=`id -u` INST_GID=`id -g`

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{_sysconfdir}
install -d $RPM_BUILD_ROOT/%{_lib}/security

# Install the nsswitch module.
%make install DESTDIR="${RPM_BUILD_ROOT}" INST_UID=`id -u` INST_GID=`id -g` \
	libdir=/%{_lib}

echo "secret" > $RPM_BUILD_ROOT/%{_sysconfdir}/ldap.secret

# Remove unpackaged file
rm -rf	$RPM_BUILD_ROOT%{_sysconfdir}/nsswitch.ldap \
	$RPM_BUILD_ROOT%{_libdir}/libnss_ldap.so.2

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/ldconfig
if [ -f /etc/init.d/nscd ]; then
	/sbin/service nscd restart >/dev/null 2>/dev/null || :
fi

%postun
/sbin/ldconfig
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


