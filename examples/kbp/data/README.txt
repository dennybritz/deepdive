Contains the data needed to run the KBP example.

entity/
	entity.sql: contains a dump for the entity() table created in prepare_data.sh. Generated after
	processing a dump of [Freebase](https://developers.google.com/freebase/data).

mention/
	mention.csv: contains the CSV data from which we will construct the mention() table specified in 
	prepare_data.sh. Has the document id, sentence id, text contents, and mention type.

training/
	positive_examples.csv: mentions that correspond to specific PERSON entities;
		contains the entity id