Ken
===========

Collects information from various sources based on defined criteria and aggregates the information for the user to see

Requirements:

	riak
	postgres
	redis
	nltk
	riak python client
	psycopg2
	requests
	flask

I took a first shot at an install script minus database installation for OS X using pip and homebrew, but the parts where I use homebrew can be replaced with another package manager or done manually.


Contains 2 Parts. The Collector and the Server


The Collector periodically goes out to the sources defined in the plugins folder (more on this later), gets data defined by the jobs in the system, puts the data in the database and indexes key words from the data.

Sources are defined in the plugins folder. Plugins must implement the AbsPlugin class's get_data function.

The Server is where jobs are defined and data is viewed by users. Uses server sent events to stream data to user.

To run:

	python collector.py
	python server.py

TODO:
    Make more distributed (i.e. plugins can run on separate machines)
    Allow for realtime collecting of data (both twitter and facebook have a realtime api, but for other plugins that might now be as feasible)
    Make proper install script

