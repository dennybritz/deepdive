Contains the data needed to run the KBP example.

entity/
	entity.sql: contains a dump for the entity() table created in prepare_data.sh.
		Generated after processing dump of [Freebase](https://developers.google.com/freebase/data).

text/
	Contains abour 28,000 raw text files (split into subdirectories of 200 files each)

training/
	training.tab: Tab-separated file where each row contains a document id, the text,
		and the entity id. The doc_id and text correspond to a specific mention, so
		this file links entities and mentions.