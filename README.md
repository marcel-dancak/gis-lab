GIS.lab - Open Source GIS office
================================
Super easy deployment of fully equipped GIS office with unlimited number of workstations in a few moments.

GIS.lab provides possibility to create fully equipped, easy-to-use, pre-configured, centrally managed, portable and unbreakable GIS office platform from one host machine running central server and unlimited number of diskless client machines. All software works out-of-box, without any need of configuration or other behind a scene knowledge, allowing users to keep high focus on their GIS task.

The platform consists from one Linux server instance running LTSP server inside automatically provisioned Virtualbox machine and unlimited diskless client machines running LTSP Fat client. This setup allows to use all client machine power and it is very friendly to server resources.

Key features:
 * super easy fully automatic deployment and maintenance - all operation are encapsulated in easy to use commands
 * nearly zero requirements for client machines - no operating system or software needed, no hard disk needed
 * no limit of number of client machines
 * 100 percent real computer user experience - no thin client glitches
 * central management of all client OS images, user accounts and user data
 * every user can log in from any client machine to get his working environment
 * unbreakable client OS images - after every client reload you always get fresh OS environment
 * rich software equipment of client machines for internet browsing, email, chat, images and video, word, spreadsheet
 and presentation editing and more
 * out of box internet sharing from host machine to all client machines
 * out of box working file sharing service (NFS)
 * out of box database server (PostgreSQL/PostGIS)
 * out of box working backup service [TODO]
 * Linux system security
 * great platform for studying open source technologies beginning from Linux OS, various system services and end user software
 * best tuned set of software equipment for data editing, analysis and database storage and management [PARTIALY IMPLEMENTED]
 * set of software equipment for scripting and GIS software development [TODO]
 * out of box working web GIS publishing solution
 * step by step manuals and how-to documents for the most common tasks [TODO]


Installation
------------
BIG FAT WARNING: Server installed to virtual machine contains its own DHCP server. DHCP server access is restricted 
by MAC addresses when GISLAB_UNKNOWN_MAC_POLICY=deny. Do not change this configuration when you are connecting to Your corporate LAN
and allways consult it with Your sysadmin.
You are absolutely safe to install with GISLAB_UNKNOWN_MAC_POLICY=allow on machine without ethernet connection to any existing LAN.

Installation will NOT modify anything on Your host machine (everything is done inside of virtual machine), no need to worry in this case.

Sofware requirements:
 * Linux (in our case XUBUNTU 12.04)
 * Virtualbox
 * Vagrant >= 1.3.3
 * Git

Download a Vagrant box
```
$ vagrant box add precise32-canonical http://cloud-images.ubuntu.com/vagrant/precise/current/precise-server-cloudimg-i386-vagrant-disk1.box
```

Download latest GIS.lab package from https://github.com/imincik/gis-lab/releases

or

clone GIS.lab sources if You are developer or familiar with Git
```
$ git clone https://github.com/imincik/gis-lab.git
```

Allow client MAC addresses in config.cfg:
 * add your MACs to GISLAB_CLIENTS_ALLOWED (recommended)
 * or set GISLAB_UNKNOWN_MAC_POLICY=allow

Fire up a Vagrant provisioner
```
$ cd gis-lab
$ vagrant up
```

Connect host machine to client machines via gigabit switch and cable (CAT 5e or higher)

Configure client machines BIOS to boot from LAN (PXE) or use boot manager (usually activated by F12 early on start) and enjoy

Do not forget to shut down GIS.lab server before shutting down host machine
```
$ vagrant halt
```


Upgrade
-------
Currently, in this phase of development we provide only hard upgrade process where whole system including data
is going to be replaced. Later we will add much more sophisticated approach. Please backup your data !

Update GIS.lab sources
```
$ git pull
```

Shutdown all client machines and destroy server
```
$ vagrant destroy
```

Install new version
```
$ vagrant up
```


IP addresses
------------
LTSP server: $GISLAB_NETWORK.5
LTSP clients: $GISLAB_NETWORK.100-250


Authentication
--------------
By default all user accounts and their password are made as simple as they can.

Server accounts (SSH)
 * vagrant:vagrant

PostgreSQL
 * lab[1-12]:lab

Default client accounts
 * lab[1-12]:lab


VirtualBox client
-----------------
Since GIS.lab 0.3 there is a full support for launching GIS.lab client in VirtualBox.
Important notes are:
 * you do not need to create any boot hard disk
 * configure boot order to boot only from network (and enable IO APIC)
 * configure network adapter in bridged mode; make sure you select the PCnet-FAST III (Am79C973)
 as the adaptor type; allow promiscuous mode for all


Plugins
-------
There is a possibility customize GIS.lab installation using plugin scripts placed in 'user/plugins/client',
'user/plugins/server' and 'user/plugins/account' directories. This files are automatically loaded at
installation process.

Server plugin can be whatever script with assigned executable permissions. It is executed after GIS.lab server
installation, before user accounts creation.

Client plugin is evaluated as LTSP plugin script (see https://wiki.edubuntu.org/HowtoWriteLTSP5Plugins).
Plugins are "sourced" not "executed", so be careful to avoid such things as "exit" in your plugin scripts.
Files must not have executable permissions set.

There are several modes in which client plugins are called:
 * commandline: builds the list of commandline arguments supported by the loaded plugins 

 * configure: sets variables for commandline options that are set 

 * before-install: before the initial chroot is built 

 * install: where the initial chroot is built (debootstrap, on debian systems) 

 * after-install: additional package installation(ltsp-client), tweaks, etc. 

 * finalization: the last steps needed, such as installing kernels, copying the kernels and network bootable images into the tftp dir, installing the server's ssh keys into the chroot, etc.

Several variables can be used in client plugins:
 * $ARCH - the servers architecture
 * $BASE - the basic directory used for ltsp chroots (defaults to /opt/ltsp)
 * $CHROOT - the name of the chroot we create in the $BASE dir (by default substituted with $ARCH)
 * $ROOT - will always point to the client dir (/opt/ltsp/$CHROOT), use it where appropriate

To execute a command in client chroot start it with 'chroot $ROOT' command.   

Account plugin can be whatever directory and files structure which will be copied to user home directory
when creating user account. It is possible to add custom configuration files or override default ones here.


Tips
----
Add secondary IP address to host machine to enable connection from host machine to client machines
```
$ ip addr add $GISLAB_NETWORK.2/24 dev eth0
```
remove it with
```
$ ip addr del $GISLAB_NETWORK.2/24 dev eth0
```


Working with GIS.lab
--------------------
### User accounts
By default, user accounts specified in GISLAB_USER_ACCOUNTS_AUTO are created automatically after installation.
You can also create or delete additional accounts manually:
 * '$ vagrant ssh -c "sudo gislab-adduser <username>"' - create account
 * '$ vagrant ssh -c "sudo gislab-deluser <username>"' - delete account


### File sharing
GIS.lab offers out-of-box file sharing solution inside its LAN. All client users can find three different shared
directories in their home directory, each one with different access policy:
 * Repository: directory with read-only permissions for users
 * Share: directory with read permissions for anybody and write permissions for file owner
 * Barrel: directory with read and write permissions for all files for all users

It is possible to mount 'Barrel' shared directory from host machine using 'utils/mount-barrel.sh' script. It is
always good idea to umount it before shutting down GIS.lab server. If forgotten try to umount it with '-fl' options.


Authors
-------
 * Ivan Mincik, GISTA s.r.o., ivan.mincik@gmail.com


Most important technologies and credits
---------------------------------------
 * VirtualBox - https://www.virtualbox.org/
 * XUBUNTU Linux - http://xubuntu.org/
 * Vagrant - http://docs.vagrantup.com/
 * LTSP - http://www.ltsp.org/
 * GDAL - http://www.gdal.org/
 * GEOS - http://geos.osgeo.org/
 * PostgreSQL - http://www.postgresql.org/
 * PgAdmin - http://www.pgadmin.org/
 * PostGIS - http://postgis.net/
 * SpatiaLite - http://www.gaia-gis.it/gaia-sins/
 * QGIS - http://www.qgis.org/
 * GRASS GIS - http://grass.osgeo.org/
 * and many more nice open source projects
