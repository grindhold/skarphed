#!/bin/bash

deb_root="./deb/skarphed-repo/"

function generate_deb {
	# generate folder structure
	mkdir -p ${deb_root}var/www/skdrepo
	mkdir -p ${deb_root}tmp/
	mkdir -p ${deb_root}etc/skdrepo
	mkdir -p ${deb_root}etc/apache2/sites-enabled/skdrepo
	mkdir -p ${deb_root}usr/share/skdrepo

	# copy your files, hack your symlinks :)
	rm -rf ${deb_root}var/www/skdrepo/common
	cp -r ../src/* ${deb_root}var/www/skdrepo/
	rm  ${deb_root}var/www/skdrepo/common
	mkdir -p ${deb_root}var/www/skdrepo/common
	cp -r ../src/common/* ${deb_root}var/www/skdrepo/common/
	cp ../gen_keypair.py ../repo_database.sql ${deb_root}tmp
	cp ../config.json ${deb_root}etc/skdrepo/
	cp ../skdrepo_apache2 ${deb_root}etc/apache2/sites-enabled/skdrepo
	cp -r ../static ${deb_root}usr/share/skdrepo/
	cp ../templates/template.html ${deb_root}usr/share/skdrepo/


	SIZE=`du -c -s ${deb_root}etc ${deb_root}tmp ${deb_root}usr ${deb_root}var | tail -n1 |  cut -f1`
	cat << EOF > ${deb_root}DEBIAN/control
Package: skarphed-repo
Priority: optional
Section: web
Installed-Size: $SIZE
Maintainer: Andre Kupka <kupka@in.tum.de>
Architecture: all
Version: 0.1
Depends: firebird2.5-super (>= 2.5), apache2 (>= 2.2), libapache2-mod-wsgi (>= 3.3), python (>= 2.6), python-pip (>= 0.7), python-dev (>= 2.6)
Description: A Skarphed Repository
EOF

	dpkg-deb -z6 -Zgzip --build ${deb_root}
	mv "./deb/skarphed-repo.deb" .
}

function generate_all {
	generate_deb
}

generate_all