# svn co http://svn.pyinstaller.org/trunk pyinstaller

PYTHON=python
GSDVIEWROOT=..
PYINSTALLERROOT=pyinstaller
DISTROOT=../dist
ONEDIRBUNDLE=$(DISTROOT)/GSDView.app
ONEFILEBUNDLE=$(DISTROOT)/onefile/GSDView.app

.PHONY: onedir onefile clean distclean html env qt

html:
	$(MAKE) -C .. html

qt:
	cp -R ../qt .

onedir: gsdview-onedir.spec html qt
	$(PYTHON) $(PYINSTALLERROOT)/pyinstaller.py $<

onefile: gsdview-onefile.spec html qt
	$(PYTHON) $(PYINSTALLERROOT)/pyinstaller.py $<

clean:
	$(RM) *.pyc logdict*.log warngsdview*.txt *~
	$(RM) -r build
	$(RM) -r $(ONEDIRBUNDLE) $(ONEFILEBUNDLE)
	$(RM) -r $(GSDVIEWROOT)/dist/onefile
	$(RM) -r $(GSDVIEWROOT)/dist/gsdview
	#if [ -d ../dist ]; then rmdir --ignore-fail-on-non-empty ../dist; fi

distclean: clean
	$(RM) -r dist qt pyinstaller gsdview_patches_applied

pyinstaller:
	git clone git://github.com/pyinstaller/pyinstaller.git
	#git clone -b master git://github.com/pyinstaller/pyinstaller.git

# @TODO: see http://www.pyinstaller.org/ticket/657
env: pyinstaller qt
	cd pyinstaller && git pull
	#cd pyinstaller/source && python waf configure build install
	if ! [ -f pyinstaller/gsdview_patches_applied ]; then \
		cd pyinstaller;\
		patch -b -N -p1 < ../patches/qt4-api2.patch;\
		touch gsdview_patches_applied;\
	fi
