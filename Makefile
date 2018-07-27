APT_INSTALL_Y = apt-get install -y
export CWD := $(shell pwd)
export PATH := $(CWD)/bin:$(PATH)
export 3GM_SCRIPTS := $(CWD)/scripts

install_scripts_requirements: scripts/requirements.txt
	pip3 install -r scripts/requirements.txt

install_app_requirements: 3gm/requirements.txt
	pip3 install -r 3gm/requirements.txt

install_tesseract_4:
	echo "Install requirements"
	$(APT_INSTALL_Y) g++
	$(APT_INSTALL_Y) autoconf automake libtool
	$(APT_INSTALL_Y) pkg-config
	$(APT_INSTALL_Y) libpng-dev
	$(APT_INSTALL_Y) libjpeg8-dev
	$(APT_INSTALL_Y) libtiff5-dev
	$(APT_INSTALL_Y) zlib1g-dev
	echo "Build leptonica"
	git clone https://github.com/DanBloomberg/leptonica
	cd leptonica
	./configure
	make
	make install
	cd ..
	echo "Done Building leptonica"
	echo "Building tesseract-ocr from git repo"
	git clone https://github.com/tesseract-ocr/tesseract
	cd tesseract
	./autogen.sh
	./configure --prefix=$HOME/local/
	make
	make install
	echo "Done building tesseract-ocr"
	echo "Downloading Tesseract Language Data"
	wget https://github.com/tesseract-ocr/tessdata_best/raw/master/ell.traineddata -P /usr/share/tesseract-ocr/tessdata/
	wget https://github.com/tesseract-ocr/tessdata_best/raw/master/eng.traineddata -P /usr/share/tesseract-ocr/tessdata/
	cd ..
	echo "Done installing tesseract"

install_chromedriver:
	cd scripts/
	echo "Installing Google Chrome"
	$(APT_INSTALL_Y) libxss1 libappindicator1 libindicator7
	wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
	dpkg -i google-chrome*.deb
	$(APT_INSTALL_Y) -f
	$(APT_INSTALL_Y) xvfb unzip
	echo "Installing Chromedriver"
	wget https://chromedriver.storage.googleapis.com/2.40/chromedriver_linux64.zip
	unzip chromedriver_linux64.zip
	chmod +x chromedriver
	rm chromedriver_linux64.zip
	echo "Linking Chromedriver"
	cp -f chromedriver /usr/local/share/chromedriver
	ln -s /usr/local/share/chromedriver /usr/local/bin/chromedriver
	ln -s /usr/local/share/chromedriver /usr/bin/chromedriver
	echo "Complete"
	cd ..

install_mongodb: install_mongo.sh
	chmod +x install_mongo.sh
	./install_mongo.sh

schedule_fetching_cronjobs: export_cronjobs.sh
	echo "Installing cron"
	$(APT_INSTALL_Y) cron
	cd scripts/
	echo "Export environment variables"
	echo $(3GM_SCRIPTS)
	echo 'export 3GM_SCRIPTS=$(3GM_SCRIPTS)' >> $(HOME)/.bashrc
	exec bash
	echo "Setup cronjobs"
	cd ..
	mkdir -p $(HOME)/GGG/pdf
	mkdir -p $(HOME)/GGG/txt
	./export_cronjobs 2 $(HOME)/GGG/pdf $(HOME)/GGG/txt

install_nlp_tools:
	echo "Installing Greek Language support for spacy"
	make install_app_requirements
	mkdir -p nlp_tools
	cd nlp_tools/
	wget https://github.com/eellak/gsoc2018-spacy/raw/6212c56f94ca3926b0959ddf9cee39df28e1c5a8/spacy/lang/el/models/el_core_web_sm-1.0.0.tar.gz
	pip3 install el_core_web_sm-1.0.0.tar.gz
	cd ..
	rm -rf nlp_tools

run_web_application_debug:
	cd 3gm/
	pkill flask
	./run.sh
	cd ..

build_codifier_pipeline:
	python3 build_pipeline.py laws links topics versions

# TODO add make install
