Ken
===========

Collects information from various sources based on defined criteria and aggregates the information for the user to see

Requirements:

	* Riak
	* Postgres
	* NLTK
	* Riak-Python-Client
	* psycopg2
	* requests
	* flask
	* gevent
	* gevent-websocket

Contains 2 Parts. The Collector and the server


The Collector periodically goes out to the sources defined in the plugins folder (more on this later), gets data defined by the jobs in the system, puts the data in the database and indexes key words from the data.

Sources are defined in the plugins folder. Plugins must implement the AbsPlugin class's get_data function.

The Server is where jobs are defined and data is viewed by users.

To run:

	* python cli.py
	* python server.py