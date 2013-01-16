Summary:	NSS library and PAM module for LDAP
Name: 		nss_ldap
Version: 	265
Release: 	6
License:	LGPL
Group:		System/Libraries
URL: 		http://www.padl.com/
BuildRequires:	openldap-devel >= 2.0.7-7.1mdk
BuildRequires:	automake
Source0:	http://www.padl.com/download/%{name}-%{version}.tar.gz
Patch0:		nss_ldap-265-Makefile.patch
Patch1:		nss_ldap-250-bind_policy_default_soft.patch
Patch2:		nss-ldap-automake-1.13.patch
Suggests:	nscd

%description
This package includes two LDAP access clients: nss_ldap and pam_ldap.
Nss_ldap is a set of C library extensions which allows X.500 and LDAP
directory servers to be used as a primary source of aliases, ethers,
groups, hosts, networks, protocol, users, RPCs, services and shadow
passwords (instead of or in addition to using flat files or NIS).

%prep
rm -rf %{buildroot}

%setup -q
%apply_patches
# first line not commented upstream for some reason
perl -pi -e 's/^ /#/' ldap.conf

%build

%serverbuild
autoreconf
export CFLAGS="%{optflags} -fPIC"
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




%changelog
* Wed May 04 2011 Oden Eriksson <oeriksson@mandriva.com> 265-4mdv2011.0
+ Revision: 666628
- mass rebuild

* Fri Dec 03 2010 Oden Eriksson <oeriksson@mandriva.com> 265-3mdv2011.0
+ Revision: 606828
- rebuild

* Wed Jun 09 2010 Buchan Milne <bgmilne@mandriva.org> 265-2mdv2010.1
+ Revision: 547801
- Suggest nscd - most setups will want it to reduce LDAP connections, and to avoid
 problems with symbol conflicts in LDAP applications with different ABI (mdv#59663)

* Fri Nov 06 2009 Guillaume Rousse <guillomovitch@mandriva.org> 265-1mdv2010.1
+ Revision: 461877
- new version
- update makefile patch
- drop unknown configure options

* Thu Sep 03 2009 Christophe Fergeau <cfergeau@mandriva.com> 264-3mdv2010.0
+ Revision: 426257
- rebuild

* Mon Mar 23 2009 Götz Waschk <waschk@mandriva.org> 264-2mdv2009.1
+ Revision: 360645
- rebuild

* Thu Jan 22 2009 Guillaume Rousse <guillomovitch@mandriva.org> 264-1mdv2009.1
+ Revision: 332535
- new version

* Thu Oct 16 2008 Buchan Milne <bgmilne@mandriva.org> 263-1mdv2009.1
+ Revision: 294443
- New version 263

* Thu Sep 04 2008 Buchan Milne <bgmilne@mandriva.org> 262-1mdv2009.0
+ Revision: 280494
- update to new version 262

* Fri Aug 15 2008 Buchan Milne <bgmilne@mandriva.org> 261-1mdv2009.0
+ Revision: 272231
- New version 261

* Tue Jun 17 2008 Thierry Vignaud <tv@mandriva.org> 259-4mdv2009.0
+ Revision: 223351
- rebuild

  + Pixel <pixel@mandriva.com>
    - do not call ldconfig in %%post/%%postun, it is now handled by filetriggers

  + Olivier Blin <oblin@mandriva.com>
    - restore BuildRoot

* Tue Dec 25 2007 Oden Eriksson <oeriksson@mandriva.com> 259-3mdv2008.1
+ Revision: 137780
- rebuilt against openldap-2.4.7 libs

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Sat Nov 17 2007 Funda Wang <fwang@mandriva.org> 259-2mdv2008.1
+ Revision: 109204
- rebuild for new lzma

* Mon Oct 29 2007 Buchan Milne <bgmilne@mandriva.org> 259-1mdv2008.1
+ Revision: 103413
- New version 259

* Mon Oct 15 2007 Buchan Milne <bgmilne@mandriva.org> 258-2mdv2008.1
+ Revision: 98510
- New version 258
- drop 3 previous patches included in new upstream version

* Mon Oct 01 2007 Andreas Hasenack <andreas@mandriva.com> 257-2mdv2008.0
+ Revision: 94171
- fix for padl #338 (nss_ldap constructs
  LDAP URIs incorrectly)
- fix for padl #332 (--enable-schema-mapping
  sets pw_change wrong)
- fix for padl #343 (nss_srv_domain does not
  take a domain, but a record)

* Fri Aug 24 2007 Andreas Hasenack <andreas@mandriva.com> 257-1mdv2008.0
+ Revision: 71049
- updated to version 257 (Closes: #32597)

* Fri Jun 22 2007 Andreas Hasenack <andreas@mandriva.com> 254-2mdv2008.0
+ Revision: 43308
- rebuild with new serverbuild (-fstack-protector)


* Thu Jan 11 2007 Buchan Milne <bgmilne@mandriva.org> 254-1mdv2007.0
+ Revision: 107664
- New version 254
- Import nss_ldap

* Wed May 03 2006 Buchan Milne <bgmilne@mandriva.org> 250-1mdk
- New release 250
- update P1

* Fri Mar 17 2006 Buchan Milne <bgmilne@mandriva.org> 249-1mdk
- New release 249
- Add P1 to default bind_policy to "soft", so as to keep previous default
  behaviour of not retyring binds to servers that are not available 
  (ie during boot).
- Fix first line of ldap.conf (Bug #21653)

* Fri Jan 20 2006 Buchan Milne <bgmilne@mandriva.org> 246-1mdk
- New release 246

* Tue Jan 17 2006 Buchan Milne <bgmilne@mandriva.org> 245-1mdk
- New release 245
- drop p1 and p2 (fixed upstream)

* Wed Dec 28 2005 Leonardo Chiquitto Filho <chiquitto@mandriva.com> 239-4mdk
- Backport two patches from 240 and 244, the last one fixes #20287

* Wed Sep 07 2005 Oden Eriksson <oeriksson@mandriva.com> 239-3mdk
- rebuild

* Wed Aug 31 2005 Buchan Milne <bgmilne@linux-mandrake.com> 239-2mdk
- Rebuild for new libldap-2.3
- buildrequire openldap-devel, not libldap-devel

* Wed Jun 29 2005 Buchan Milne <bgmilne@linux-mandrake.com> 239-1mdk
- New release 239
- rpmbuildupdate-able
- drop db patches (db is no longer used)

* Tue May 31 2005 Stefan van der Eijk <stefan@eijk.nu> 220-6mdk
- split off pam_ldap into seperate package
- libtoolize (thanks Oden!)

* Fri Mar 11 2005 Pascal Terjan <pterjan@mandrake.org> 220-5mdk
- don't break using uri with patch 3 (#7551)

* Fri Feb 04 2005 Buchan Milne <bgmilne@linux-mandrake.com> 220-4mdk
- rebuild for ldap2.2_7

* Mon Aug 23 2004 Luca Berra <bluca@vodka.it> 220-3mdk 
- buildrequre autoconf-2.1 and automake-1.4
- force autoreconf

* Fri Aug 13 2004 Luca Berra <bluca@vodka.it> 220-2mdk 
- use libdb_nss 4.2
- pam_ldap 170

* Thu Jul 01 2004 Florin <florin@mandrakesoft.com> 220-1mdk
- nss_ldap 220
- remove the useless version and noent patches

* Thu Apr 29 2004 Florin <florin@mandrakesoft.com> 217-1mdk
- nss_ldap 217
- pam_ldap 169
- add the noent and version patches
- remove the 150 db3 obsolete patch

