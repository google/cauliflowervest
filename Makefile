#
# Copyright 2011 Google Inc. All Rights Reserved.
#

CV_VERSION=0.8.2
CV=cauliflowervest-${CV_VERSION}
CV_DIST=dist/${CV}.tar
CV_SDIST=${CV_DIST}.gz
KEYCZAR_VERSION=0.7b.081911
KEYCZAR_SRC=python-keyczar-${KEYCZAR_VERSION}.tar.gz
KEYCZAR_BUILD=build/python-keyczar-0.7b.macosx-10.7-intel.tar.gz
CSFDE_BIN=src/csfde/build/Default/csfde
CONTENTS_TAR_GZ=build/contents.tar.gz
CWD=$(shell pwd)

os_check:
	sw_vers 2>&1 >/dev/null || ( echo This package requires OS X. ; exit 1 )
	sw_vers -productVersion | egrep -q '^10\.7\.' || \
	( echo This package requires OS X 10.7. ; exit 1 )

test: os_check keyczar
	# This strange import fixes some kind of race condition in the
	# way that encodings.utf_8 retains its import of the codecs module.
	#
	# If we import encodings.utf_8 before google_test starts,
	# it will import properly and be replaced between each module
	# run when google_apputils does sys.modules cleanup.
	#
	# Related to https://bugs.launchpad.net/launchpad/+bug/491705
	# and the other bugs referenced there, I believe.
	#
	python -c \
	'import encodings.utf_8; import sys; sys.argv=["setup.py","google_test"]; import setup'

build: os_check
	python setup.py build

install: client_config build
	python setup.py install

clean:
	rm -rf dist build tmp

${CV_SDIST}: clean client_config
	python setup.py sdist --formats=tar
	gzip ${CV_DIST}

client_config:
	@echo client_config

server_config: build keyczar
	./create_gae_bundle.sh ${CWD}

tmp/${KEYCZAR_SRC}:
	mkdir -p tmp
	curl -o $@ http://keyczar.googlecode.com/files/${KEYCZAR_SRC}

keyczar: tmp/${KEYCZAR_SRC}
	mkdir -p build
	mkdir -p tmp/keycz
	rm -rf ../../../build/keyczar
	tar -zxf tmp/${KEYCZAR_SRC} -C tmp/keycz
	cd tmp/keycz/python-keyczar-* ; \
	python setup.py install --prefix . ; \
	mv lib/python*/site-packages/keyczar ../../../build ; \
	ln -f -s ../build/keyczar ../../../src/keyczar

${CSFDE_BIN}: os_check src/csfde/csfde.mm
	cd src/csfde ; \
	xcodebuild -project csfde.xcodeproj

csfde: ${CSFDE_BIN}

${CONTENTS_TAR_GZ}: csfde
	# begin create tmpcontents
	mkdir -p build
	# add csfde
	mkdir -p tmp/contents/usr/local/bin
	cp ${CSFDE_BIN} tmp/contents/usr/local/bin/
	chmod 755 tmp/contents/usr/local/bin/csfde
	# end, create tarball
	cd tmp/contents && tar -cf ../../build/contents.tar .
	gzip build/contents.tar

${CV}.dmg: ${CV_SDIST} ${CONTENTS_TAR_GZ}
	mkdir -p dist
	rm -f dist/$@
	./tgz2dmg.sh ${CONTENTS_TAR_GZ} dist/$@ \
	-id com.google.code.cauliflowervest \
	-version ${CV_VERSION} \
	-r ${CV_SDIST} \
	-s postflight

${CV}.pkg: ${CV_SDIST} ${CONTENTS_TAR_GZ}
	mkdir -p dist
	rm -rf dist/$@
	./tgz2dmg.sh ${CONTENTS_TAR_GZ} dist/$@ \
	-pkgonly \
	-id com.google.code.cauliflowervest \
	-version ${CV_VERSION} \
	-r ${CV_SDIST} \
	-s postflight

pkg: ${CV}.pkg

dmg: ${CV}.dmg

release: server_config
	appcfg.py update gae_bundle/
