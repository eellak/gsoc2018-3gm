APT_INSTALL_Y = apt-get install -y
export CWD := $(shell pwd)
export PATH := $(CWD)/bin:$(PATH)
export 3GM_SCRIPTS := $(CWD)/scripts
export 3GM_TOOLS := $(CWD)/3gm/tools

# Install script requirements
install_scripts_requirements: scripts/requirements.txt
	pip3 install -r scripts/requirements.txt

# Install core functionality requirements
install_app_requirements: 3gm/requirements.txt
	pip3 install -r 3gm/requirements.txt

# Install Google Tesseract OCR Engine v4
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
	cd leptonica && ./configure && make && make install
	echo "Done Building leptonica"
	echo "Building tesseract-ocr from git repo"
	git clone https://github.com/tesseract-ocr/tesseract
	cd tesseract && ./autogen.sh && ./configure --prefix=$HOME/local/ && make && make install
	echo "Done building tesseract-ocr"
	echo "Downloading Tesseract Language Data"
	wget https://github.com/tesseract-ocr/tessdata_best/raw/master/ell.traineddata -P /usr/share/tesseract-ocr/tessdata/
	wget https://github.com/tesseract-ocr/tessdata_best/raw/master/eng.traineddata -P /usr/share/tesseract-ocr/tessdata/
	echo "Done installing tesseract"

# Install chromedriver
install_chromedriver:
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
	mv chromedriver scripts/chromedriver
	echo "Complete"

# Install MongoDB from Community PPA
install_mongodb: install_mongo.sh
	chmod +x install_mongo.sh
	./install_mongo.sh

# Schedule cron jobs for fetching and conversion
schedule_fetching_cronjobs: export_cronjobs.sh
	echo "Installing cron"
	$(APT_INSTALL_Y) cron
	echo "Export environment variables"
	echo $(3GM_SCRIPTS)
	echo 'export 3GM_SCRIPTS=$(3GM_SCRIPTS)' >> $(HOME)/.bashrc
	exec bash
	echo "Setup cronjobs"
	mkdir -p $(HOME)/GGG/pdf
	mkdir -p $(HOME)/GGG/txt
	./export_cronjobs 2 $(HOME)/GGG/pdf $(HOME)/GGG/txt

# Install spacy and nlp tools
install_nlp_tools:
	echo "Installing Greek Language support for spacy"
	make install_app_requirements
	wget https://github.com/eellak/gsoc2018-spacy/raw/6212c56f94ca3926b0959ddf9cee39df28e1c5a8/spacy/lang/el/models/el_core_web_sm-1.0.0.tar.gz
	pip3 install el_core_web_sm-1.0.0.tar.gz

# Run flask web app
run_web_application:
	echo "Running web application"
	cd 3gm;	pkill flask; ./run.sh

# Build codifier pipeline
codifier_pipeline:
	echo "Building codifier full pipeline"
	python3 build_pipeline.py laws links topics versions

# Run tests
run_codifier_tests:
	echo "Running codifier tests"
	cd 3gm && pytest tests.py -vv

# Symlink CLI Tools
symlink_tools:
	echo "Symlinking tools"
	ln -s $(3GM_TOOLS)/law_codifier.py /usr/local/bin/law_codifier.py
	ln -s $(3GM_TOOLS)/exporter.py /usr/local/bin/exporter.py
	echo "Symlinking done"

# Core functionality
core: install_app_requirements install_nlp_tools

# Scripts
scripts: install_scripts_requirements install_tesseract_4 install_chromedriver install_mongodb

# Make all targets
all: core scripts

# Make docs with pydoc
docs:
	cd 3gm && pydoc3 -w syntax
	cd 3gm && pydoc3 -w database
	cd 3gm && pydoc3 -w codifier
	cd 3gm && pydoc3 -w pparser
	cd 3gm && pydoc3 -w apply_links
	cd 3gm && pydoc3 -w summarize
	cd 3gm && pydoc3 -w app
	cd 3gm && pydoc3 -w phrase_fun
	cd 3gm && mv syntax.html ../docs/
	cd 3gm && mv database.html ../docs/
	cd 3gm && mv codifier.html ../docs/
	cd 3gm && mv pparser.html ../docs/
	cd 3gm && mv apply_links.html ../docs/
	cd 3gm && mv summarize.html ../docs/
	cd 3gm && mv app.html ../docs/
	cd 3gm && mv phrase_fun.html ../docs/
