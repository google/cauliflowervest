#
# Copyright 2011 Google Inc. All Rights Reserved.
#

CV_VERSION=0.9.3
CV=cauliflowervest-${CV_VERSION}
CV_DIST=dist/${CV}.tar
CV_SDIST=${CV_DIST}.gz
KEYCZAR_VERSION=0.7b.081911
KEYCZAR_SRC=python-keyczar-${KEYCZAR_VERSION}.tar.gz
CSFDE_BIN=src/csfde/build/Default/csfde
CONTENTS_TAR_GZ=build/contents.tar.gz
CWD=$(shell pwd)
PYTHON_VERSION=2.7
PYTHON=$(shell type -p python${PYTHON_VERSION})
INSTALL_DIR=/usr/local/cauliflowervest/
VE_DIR=cv

os_check:
	@sw_vers >/dev/null 2>&1 || ( echo This package requires OS X. ; exit 1 )
	@sw_vers -productVersion | egrep -q '^10\.[^1-6]' || \
	( echo This package requires OS X 10.7 or later. ; exit 1 )

python_check:
	@if [ ! -x "${PYTHON}" ]; then echo Cannot find ${PYTHON} ; exit 1 ; fi

virtualenv: python_check
	${PYTHON} -c 'import virtualenv' || \
	sudo easy_install-${PYTHON_VERSION} -U virtualenv

VE: virtualenv python_check
	[ -d VE ] || \
	${PYTHON} $(shell type -p virtualenv) --no-site-packages VE

test: os_check VE keyczar
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
	VE/bin/python -c \
	'import encodings.utf_8; import sys; sys.argv=["setup.py","google_test"]; import setup' && echo ALL TESTS COMPLETED SUCCESSFULLY

build: VE os_check
	VE/bin/python setup.py build

install: client_config build
	VE/bin/python setup.py install

clean:
	rm -rf dist build tmp

${CV_SDIST}: clean VE client_config
	VE/bin/python setup.py sdist --formats=tar
	gzip ${CV_DIST}

client_config:
	@echo client_config

server_config: build keyczar
	./create_gae_bundle.sh ${CWD}

tmp/${KEYCZAR_SRC}:
	mkdir -p tmp
	curl -o $@ http://keyczar.googlecode.com/files/${KEYCZAR_SRC}

keyczar: VE tmp/${KEYCZAR_SRC}
	mkdir -p build
	mkdir -p tmp/keycz
	rm -rf ../../../build/keyczar
	tar -zxf tmp/${KEYCZAR_SRC} -C tmp/keycz
	cd tmp/keycz/python-keyczar-* ; \
	../../../VE/bin/python setup.py install

${CSFDE_BIN}: os_check src/csfde/csfde.mm
	@if [ ! @sw_vers -productVersion | egrep -q '^10\.7' ]; then \
		cd src/csfde ; \
		xcodebuild -project csfde.xcodeproj ; \
	fi

csfde: ${CSFDE_BIN}

${CONTENTS_TAR_GZ}: csfde
	# begin create tmpcontents
	mkdir -p build
	# add /usr/local/bin/{csfde,cauliflowervest}.
	mkdir -p tmp/contents/usr/local/bin
	@if [ ! @sw_vers -productVersion | egrep -q '^10\.7' ]; then \
		cp ${CSFDE_BIN} tmp/contents/usr/local/bin/ ; \
		chmod 755 tmp/contents/usr/local/bin/csfde ; \
	fi
	ln -s ${INSTALL_DIR}/${VE_DIR}/bin/cauliflowervest tmp/contents/usr/local/bin/cauliflowervest
	# add the directory that virtualenv will setup into
	mkdir -p tmp/contents/${INSTALL_DIR}/${VE_DIR}
	chmod -R 755 tmp/contents/${INSTALL_DIR}
	# end, create tarball
	cd tmp/contents && tar -cf ../../build/contents.tar .
	gzip build/contents.tar

install_name_tool:
	cp /usr/bin/install_name_tool .

vep: install_name_tool

${CV}.dmg: ${CV_SDIST} ${CONTENTS_TAR_GZ} vep
	mkdir -p dist
	rm -f dist/$@
	./tgz2dmg.sh ${CONTENTS_TAR_GZ} dist/$@ \
	-id com.google.code.cauliflowervest \
	-version ${CV_VERSION} \
	-pyver ${PYTHON_VERSION} \
	-vep install_name_tool \
	-r ${CV_SDIST} \
	-R PyYAML*.egg \
	-R google_apputils-*.egg \
	-R pyasn1-*.egg \
	-R python_dateutil-*.egg \
	-R python_gflags-*.egg \
	-R pytz-*.egg \
	-R simplejson*.egg \
	-s postflight \
	-s roots.pem

${CV}.pkg: ${CV_SDIST} ${CONTENTS_TAR_GZ} vep
	mkdir -p dist
	rm -rf dist/$@
	./tgz2dmg.sh ${CONTENTS_TAR_GZ} dist/$@ \
	-pkgonly \
	-id com.google.code.cauliflowervest \
	-version ${CV_VERSION} \
	-pyver ${PYTHON_VERSION} \
	-vep install_name_tool \
	-r ${CV_SDIST} \
	-R PyYAML*.egg \
	-R google_apputils-*.egg \
	-R pyasn1-*.egg \
	-R python_dateutil-*.egg \
	-R python_gflags-*.egg \
	-R pytz-*.egg \
	-R simplejson*.egg \
	-s postflight \
	-s roots.pem

pkg: ${CV}.pkg

dmg: ${CV}.dmg

release: server_config
	appcfg.py update gae_bundle/
