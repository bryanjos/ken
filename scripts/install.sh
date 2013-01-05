#!/usr/bin/sh

brew update && brew install redis && brew install mongo
sudo pip install flask
sudo pip install pymongo
sudo pip install redis
sudo pip install -U pyyaml nltk
sudo python -m nltk.downloader -d /usr/share/nltk_data all
