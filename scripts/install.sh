#!/usr/bin/sh

brew update && brew install redis
sudo pip install flask
sudo pip install riak
sudo pip install psycopg2
sudo pip install redis
sudo pip install -U pyyaml nltk
sudo python -m nltk.downloader -d /usr/share/nltk_data all

echo "Run create_db.sql, found in this folder, on a postgres db."
echo "Information on installing Riak can be found at http://docs.basho.com/riak/latest/tutorials/installation/"
