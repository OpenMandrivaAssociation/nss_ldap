%global nssdir /%{_lib}
%global pamdir /%{_lib}/security

%define _hardened_build 1

Name:           nss_ldap
Version:        0.9.10
Release:        1%{?dist}
Summary:        An nsswitch module which uses directory servers
License:        LGPLv2+
URL:            http://arthurdejong.org/nss-pam-ldapd/
Source0:        http://arthurdejong.org/nss-pam-ldapd/nss-pam-ldapd-%{version}.tar.gz
Source1:        http://arthurdejong.org/nss-pam-ldapd/nss-pam-ldapd-%{version}.tar.gz.sig
Source3:        nslcd.tmpfiles
Source4:        nslcd.service

# Pylint tests fail w/o certain imports and are not needed for nslcd anyway,
# plus, we don't ship the python utilities
Patch0001:      0001-Disable-pylint-tests.patch
Patch0002:      0002-Watch-for-uint32_t-overflows.patch

BuildRequires:  openldap-devel, krb5-devel
BuildRequires:  autoconf, automake
BuildRequires:  pam-devel
BuildRequires:  systemd-units
%{?systemd_requires}

# Pull in nscd, which is recommended.
Recommends:     nscd

Obsoletes:      nss-ldapd < 0.7
Provides:       nss-ldapd = %{version}-%{release}

# Obsolete PADL's nss_ldap
Provides:       nss_ldap = 265-12
Obsoletes:      nss_ldap < 265-11

# Obsolete PADL's pam_ldap
Provides:       pam_ldap = 185-15
Obsoletes:      pam_ldap < 185-15

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
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/{%{_libdir},%{_unitdir}}
install -p -m644 %{SOURCE4} $RPM_BUILD_ROOT/%{_unitdir}/

ln -s libnss_ldap.so.2 $RPM_BUILD_ROOT/%{nssdir}/libnss_ldap.so

sed -i -e 's,^uid.*,uid nslcd,g' -e 's,^gid.*,gid ldap,g' \
$RPM_BUILD_ROOT/%{_sysconfdir}/nslcd.conf
touch -r nslcd.conf $RPM_BUILD_ROOT/%{_sysconfdir}/nslcd.conf
mkdir -p -m 0755 $RPM_BUILD_ROOT/var/run/nslcd
mkdir -p -m 0755 $RPM_BUILD_ROOT/%{_tmpfilesdir}
install -p -m 0644 %{SOURCE3} $RPM_BUILD_ROOT/%{_tmpfilesdir}/%{name}.conf

%files
%doc AUTHORS ChangeLog COPYING HACKING NEWS README TODO
%{_sbindir}/*
%{nssdir}/*.so*
%{pamdir}/pam_ldap.so
%{_mandir}/*/*
%attr(0600,root,root) %config(noreplace) %verify(not md5 size mtime) /etc/nslcd.conf
%attr(0644,root,root) %config(noreplace) %{_tmpfilesdir}/%{name}.conf
%{_unitdir}/nslcd.service
%attr(0775,nslcd,root) /var/run/nslcd

%pre
getent group  ldap  > /dev/null || \
/usr/sbin/groupadd -r -g 55 ldap
getent passwd nslcd > /dev/null || \
/usr/sbin/useradd -r -g ldap -c 'LDAP Client User' \
    -u 65 -d / -s /sbin/nologin nslcd 2> /dev/null || :

%post
# The usual stuff.
/sbin/ldconfig
%systemd_post nslcd.service

%preun
%systemd_preun nslcd.service

%postun
/sbin/ldconfig
%systemd_postun_with_restart nslcd.service
