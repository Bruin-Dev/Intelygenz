buntu@ip-172-31-29-18:~$ cat /usr/share/doc/ubuntu-commoncriteria/README
ubuntu-commoncriteria -- Common Criteria EAL2 Scripts and Packages
==================================================================
Version 1.0.18.04.1

ubuntu-commoncriteria contains the necessary scripts and packages to
put an Ubuntu 18.04.4 LTS (Server) system into the certified
Common Criteria EAL2 evaluated configuration.

Overview
========
ubuntu-commoncriteria installs the following into /usr/lib/common-criteria:

 * a tarball, Ubuntu-18.04-Common-Criteria.tar.gz, containing additional,
   required Ubuntu 18.04.4 packages that are not found on the
   Ubuntu 18.04.4 ISO. The tarball also contains the required
   post-install scripts that configure the system into the certified
   EAL2 evaluated configuration.

 * a main configure script, Configure-Ubuntu-Common-Criteria.sh,
   that installs the packages in the tarball and runs each of the
   post install scripts.

 * Evaluated Configuration Guide provides guidance on setting up and
   using the system.

 * This README

Because the system to be setup into the EAL2 evaluated configuration
needs to be disconnected from any hostile network during installation
and configuration, it is likely the ubuntu-commoncriteria package will
have to be downloaded and installed on a different system, which is
connected to the internet. The tarball and the main script can then
be transferred to the system to be setup into the EAL2 evaluated
configuration via an off-line mechanism, e.g. by using removable
storage media like a USB stick or the use of scp or other secure options.

The system to be setup must be newly installed with Ubuntu 18.04.4 LTS
following the instructions and guidelines in section
"2.2.3 Standard Installation of Ubuntu" of the Evaluated
Configuration Guide.

The execution of the main script requires root privileges.
(The following is all on one line.)

  sudo Configure-Ubuntu-Common-Criteria.sh
       Ubuntu-18.04-Common-Criteria.tar.gz

All questions MUST be answered with "y"es to put the system into
the EAL2 evaluated configuration. After successful execution of the
main script, the system must be rebooted to ensure that all
settings and software applied to the system take effect. For more
information, please refer to section "2.2.4 Achieving the Evaluated
Configuration" in the Evaluated Configuration Guide.
