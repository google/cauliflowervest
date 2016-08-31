#
# Copyright 2011 Google Inc. All Rights Reserved.
#

CV_VERSION=0.10.2
CV=cauliflowervest-${CV_VERSION}
CV_DIST=dist/${CV}.tar
CV_SDIST=${CV_DIST}.gz
KEYCZAR_VERSION=0.716
CSFDE_BIN=src/csfde/build/Default/csfde
CONTENTS_TAR_GZ=build/contents.tar.gz
CWD=$(shell pwd)
IS_OSX=$(type -p sw_vers > /dev/null ; echo $?)
PRODUCT_VERSION=$(shell sw_vers -productVersion 2>/dev/null | cut -d. -f1-2)
OSX_LION=$(shell sw_vers -productVersion 2>/dev/null | egrep -q '^10\.7' && echo 1 || echo 0)
PYTHON_VERSION=2.7
PYTHON=$(shell which python${PYTHON_VERSION})
INSTALL_DIR=/usr/local/cauliflowervest/
VE_DIR=cv
BUILD_VERSION=$(shell (git rev-parse HEAD 2>/dev/null || echo ${CV_VERSION} | tr '.' '-') | cut -c1-12)
SDK_INCLUDE=/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX${PRODUCT_VERSION}.sdk/usr/include/
XQUARTZ_INCLUDE_X11=/opt/X11/include/X11

python_check:
	@if [ ! -x "${PYTHON}" ]; then echo Cannot find ${PYTHON} ; exit 1 ; fi

virtualenv: python_check
	sudo easy_install-${PYTHON_VERSION} -U virtualenv==1.10.1

VE: virtualenv python_check
	[ -d VE ] || \
	$(shell which virtualenv-${PYTHON_VERSION}) --no-site-packages VE

xlib_include:
	@[ "${IS_OSX}" = "0" ] && \
	[ -d ${SDK_INCLUDE} ] && \
	[ -d ${XQUARTZ_INCLUDE_X11} ] && \
	[ ! -L ${SDK_INCLUDE}/X11 ] && \
	sudo ln -sf ${XQUARTZ_INCLUDE_X11} ${SDK_INCLUDE}/X11 || \
	echo not OS X, no symlink can be created or SDK directory found.

src/tests/gae_server.zip:
	rm -Rf tmp/gae_server
	mkdir -p tmp/gae_server
	# TODO(maximermilov): current master of appengine-python-vm-runtime
	#                     changed directory structure. switch to master
	#                     after release.
	curl -o tmp/master.zip https://codeload.github.com/GoogleCloudPlatform/python-compat-runtime/zip/2e87623349618e38799cae9ed62227b6f56ae00b
	unzip -q tmp/master.zip -d tmp/gae_server
	cd tmp/gae_server/python-compat-runtime-*/python_vm_runtime/ && zip -q -r ../../../../src/tests/gae_server.zip *

test: VE keyczar xlib_include src/tests/gae_server.zip
	# Hack for Pillow installation
	VE/bin/python setup.py test
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

update_bower_deps:
	bower update -q
	rm -Rf src/cauliflowervest/server/components
	mkdir src/cauliflowervest/server/components
	cp -R bower_components/* src/cauliflowervest/server/components

update_npm_deps:
	# package.json force npm to install package even if it installed globally or in higher level directories
	echo "{}" > package.json
	npm install --force npm
	node_modules/.bin/npm install google-closure-library gulp-vulcanize shelljs del gulp gulp-rename

build_app: update_npm_deps update_bower_deps
	node_modules/gulp/bin/gulp.js vulcanize

build: build_app VE
	VE/bin/python setup.py build

install: client_config build
	VE/bin/python setup.py install

clean:
	rm -rf dist build tmp VE *.egg node_modules bower_components

${CV_SDIST}: clean VE client_config
	VE/bin/python setup.py sdist --formats=tar
	gzip ${CV_DIST}

client_config:
	@echo client_config

server_config: build test keyczar
	./create_gae_bundle.sh ${CWD}

keyczar: VE
	VE/bin/pip install python-keyczar==${KEYCZAR_VERSION}

${CSFDE_BIN}: src/csfde/csfde.mm
	# The csfde tool is specifically neeeded for Lion/10.7 only.  Starting at
	# 10.8, fdesetup is available and used instead.
	@if [ ${OSX_LION} == 1 ]; then \
		cd src/csfde ; \
		xcodebuild -project csfde.xcodeproj ; \
	fi

csfde: ${CSFDE_BIN}

${CONTENTS_TAR_GZ}: csfde
	# begin create tmpcontents
	mkdir -p build
	# add /usr/local/bin/{csfde,cauliflowervest}.
	mkdir -p tmp/contents/usr/local/bin
	@if [ ${OSX_LION} == 1 ]; then \
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
	appcfg.py --version=${BUILD_VERSION} update gae_bundle/
	appcfg.py --version=${BUILD_VERSION} set_default_version gae_bundle/
