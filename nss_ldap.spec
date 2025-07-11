%global		nssdir %{_libdir}
%global		pamdir %{_libdir}/security

%define		_hardened_build 1

Name:		nss_ldap
Version:		0.9.12
Release:		5
Summary:	An nsswitch module which uses directory servers
License:	LGPLv2+
URL:		https://arthurdejong.org/nss-pam-ldapd/
Source0:	http://arthurdejong.org/nss-pam-ldapd/nss-pam-ldapd-%{version}.tar.gz
Source1:	http://arthurdejong.org/nss-pam-ldapd/nss-pam-ldapd-%{version}.tar.gz.sig
Source3:	nslcd.tmpfiles
Source4:	nslcd.service
# Pylint tests fail w/o certain imports and are not needed for nslcd anyway,
# plus, we don't ship the python utilities
Patch0001:	0001-Disable-pylint-tests.patch
Patch0002:	0002-Watch-for-uint32_t-overflows.patch

BuildRequires:	pkgconfig(ldap)
BuildRequires:	krb5-devel
BuildRequires:	autoconf, automake
BuildRequires:	pam-devel
BuildRequires:	systemd-rpm-macros
%{?systemd_requires}
Requires(pre):	glibc
Requires(pre):	shadow

# Pull in nscd, which is recommended.
Recommends:	nscd

Obsoletes:	nss-ldapd < 0.7
Provides:	nss-ldapd = %{version}-%{release}

# Obsolete PADL's pam_ldap
Provides:	pam_ldap = 186-15
Obsoletes:	pam_ldap < 186-15

%description
The nss-pam-ldapd daemon, nslcd, uses a directory server to look up name
service information (users, groups, etc.) on behalf of a lightweight
nsswitch module.

%prep
%autosetup -n nss-pam-ldapd-%{version} -p1
autoreconf -f -i

%build
%configure --libdir=%{nssdir} \
           --disable-utils \
           --with-pam-seclib-dir=%{pamdir}

%make_build

%check
make check

%install
make install DESTDIR=%{buildroot}
mkdir -p %{buildroot}/{%{_libdir},%{_unitdir}}
install -p -m644 %{SOURCE4} %{buildroot}%{_unitdir}/

ln -s libnss_ldap.so.2 %{buildroot}/%{nssdir}/libnss_ldap.so

sed -i -e 's,^uid.*,uid nslcd,g' -e 's,^gid.*,gid ldap,g' \
%{buildroot}%{_sysconfdir}/nslcd.conf
touch -r nslcd.conf %{buildroot}%{_sysconfdir}/nslcd.conf
mkdir -p -m 0755 %{buildroot}/var/run/nslcd
mkdir -p -m 0755 %{buildroot}%{_tmpfilesdir}
install -p -m 0644 %{SOURCE3} %{buildroot}%{_tmpfilesdir}/%{name}.conf

mkdir -p %{buildroot}%{_sysusersdir}
cat >%{buildroot}%{_sysusersdir}/%{name}.conf <<EOF
g ldap 55
u nslcd 65:55 "LDAP Client User" / %{_sbindir}/nologin
EOF

%files
%doc AUTHORS ChangeLog COPYING HACKING NEWS README TODO
%{_sbindir}/*
%{nssdir}/*.so*
%{pamdir}/pam_ldap.so
%{_mandir}/*/*
%attr(0600,root,root) %config(noreplace) %verify(not md5 size mtime) /etc/nslcd.conf
%attr(0644,root,root) %config(noreplace) %{_tmpfilesdir}/%{name}.conf
%{_unitdir}/nslcd.service
%attr(0775,nslcd,ldap) /var/run/nslcd
%{_sysusersdir}/%{name}.conf
