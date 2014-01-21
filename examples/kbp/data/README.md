Contains the data needed to run the KBP example.

qid_to_mid.csv: contains the query id -> mention id mapping necessary to translate between
	the KBP-provied training/evaluation data and our database.

entity/
	entity.sql: contains a dump for the entity() table created in prepare_data.sh.
		Generated after processing dump of [Freebase](https://developers.google.com/freebase/data).

	eid_to_fid.tsv: contains tha mapping between entity id's used in the provided KBP data
		(training, evaluation) and the freebase id's used in the entity() table.

	examples/kbp/prepare_data.sh loads these tables into the database

evaluation/
	Contains the data necessary to evaluate the performance of the system.

	evaluation_entity_linking_queries.xml: contains the query id, name (text contents), and
		document id for queries on which we want to evaluate performance. This data is
		processed in processing/... and is converted to CSV format 

	evaluation_entity_linking_query_types.tab: contains the query id, entity id, and entity type
		which we can use to construct a table with query id, entity id, mention id

mention/
	Contains the CSV data from which we will construct the mention() table specified in 
	prepare_data.sh. Has the document id, sentence id, text contents, and mention type.

	examples/kbp/prepare_data.sh loads this into the database

training/
	Contains the data necessary to train the system.

	training_entity_linking_queries.xml: contains the query id, name (text contents),
		document id, and entity id for queries on which we want to evaluate performance.
		This data is processed in processing/... and is converted to CSV format, and is located
		in training/training_data.csv

	training_entity_linking_query_types.tab: contains the query id, entity id, and entity type
		which we can use to construct a table with query id, entity id, mention id