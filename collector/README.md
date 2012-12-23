Collector
===========

The collector periodically will for each information source

	*  	get all active jobs in the system
	*	get information from the current information source and put them in the database
	*	take that information and index words, nouns, sentences into riak
		* Data riak will be like this
			Bucket Name location
				Key: location
				Value: {data: <location>, IDs:[<ID>]}

			Bucket Name sentences
				Key: sentence hash
				Value: {data: <sentence_hash>, IDs:[<ID>]}

			Bucket Name words
				Key: word hash
				Value: {data: <word_hash>, IDs:[<ID>]}

			Bucket Name nouns
				Key: noun hash
				Value: {data: <noun_hash>, IDs:[<ID>]}

	*	for each job, a last time job ran will be used to get data since then


The server will be where jobs are CRUDed and data is shown.

The server will query the riak database for the relevant Ids. Once those Ids are recieved,
the data is collected from the postgres database based on time, location, lat, lon, and distance from.

Once this data is collected, text analysis will be used based on the tags in the job in order to cull down results
to more relevant info.

Data is paged. This should allow for text analysis on a small amount of data at a time. 