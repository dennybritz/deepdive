---
layout: default
---

# Getting Started

### Dependencies

In addition to the DeepDive dependencies, you will need the following libraries to run this example (used in udf/extract_features.py and in udf/extract_mentions.py):
* [NLTK](http://nltk.org/)
* [Python-ngram](https://code.google.com/p/python-ngram/)

### Downloading and Compiling

Download the DeepDive system and make sure it compiles locally and passes the tests (see the [Installation Guide]()).

### Creating a New Example

To create a new example that runs the DeepDive system, follow these steps:
- Create a folder in the examples directory
- Create the file *application.conf* - this is a configuration file that tells DeepDive what steps to take (the details on what to include in this file are below).
- (Recommended) Create the script *prepare_data.sh* which processes any existing raw data as necessary and loads the processed data into the PostgreSQL database.
- (Recommended) Create the script *run.sh* which runs DeepDive and any data processing that must happen beforehand (*run.sh* will execute *prepare_data.sh*). Thus, to run DeepDive on the example, you can simply execute *run.sh*. Note that all the examples provided include both files.
- The folder may also contain any auxiliary scripts or folders; for example, most applications will require extractors, which by convention are placed into a udf/ directory.

We will now walk through the steps needed to create all of these files for a specific example.

# Overview

To illustrate a concrete application of DeepDive, we provide a simple example of [entity linking](), located in examples/kbp. This example is taken from the [KBP entity linking competition](http://www.nist.gov/tac/2013/KBP/EntityLinking/). The objective of the competition is to extract mentions of the type PERSON, ORGANIZATION, or GPE (geo-political entity) from a corpus of text documents, and to link these mentions to known Wikipedia entities.

For illustrative purposes, we will extract only PERSON mentions from a corpus of news articles (located in data/text) and link them to PERSON entities (a PostgreSQL table of these entities is in data/entity/entity.sql).

Since our objective is to figure out whether a given (entity, mention) pair should be linked, the inference variable is the column *is_correct* in the *candidate_link()* table. To perform linking, a training set of known (entity, mention) links is used to learn the association between possible (entity, mention) pairs. DeepDive uses the links in the training set to infer associations between unknown links. 

DeepDive extracts features from the entity and mention text, and then performs probabilistic inference on the (entity, mention) variables.

At a high level, the following tasks are performed:
1. Data loading
2. Candidate link extraction
3. Adding training examples
4. Feature extraction
5. Inference
6. Evaluation


### 1. Data Loading

(see data/README.txt)

The script prepare_data.sh creates and populates the necessary tables from the provided SQL and CSV files.

    [include the script]


### 2. Candidate Link Extraction

To begin the process of inferring whether or not a particular (entity, mention) pair should be linked, we must first arrive at a list of candidate (entity, mention) pairs that will be used as input to the feature extraction step. A good initial guess for this would be all possible (entity, mention) combinations, given all the mentions and entities in our input data. However, the number of such pairs scales poorly with data set size, so this approach is impractical. Therefore to extract candidate pairs we perform a theta join on the mention and entity tables (comparing the text_contents fields):

    SELECT * FROM mention INNER JOIN entity ON (
              lower(mention.text_contents) = lower(entity.text_contents) OR
              levenshtein(lower(mention.text_contents), lower(entity.text_contents)) < 2 OR
              position(lower(mention.text_contents) in lower(entity.text_contents)) >= 0 OR
              position(lower(entity.text_contents) in lower(mention.text_contents)) >= 0)

An entry in the *candidate_link* table is created if there exists a (mention, entity) pair such that any of the following conditions hold:
- their lowercase text matches exactly
- their [Levenshtein distance](http://en.wikipedia.org/wiki/Levenshtein_distance) is less than a threshold
- one is a substring of the other


### 3. Adding Training Examples

Once the candidate links are determined, training data is added to guide the inference. We can think of the training data as a set of (entity, mention) pairs which are known to be linked. Thus, after loading the training data from file, we can update our *candidate_link* table by inserting appropriate values into the *is_correct* column.


### 4. Feature extraction

Once the candidate (entity, mention) pairs are found and the training data is loaded, feature extraction is performed for each candidate (e, m) pair. In our example, features are binary indicators of whether certain predicates are true. The output of this step is the *link_feature* relation: ```link_feature(entity_id, mention_id, feature_type)``` where *feature_type* is a string name representing a particular feature (e.g. exact_string_match). Note that the feature extration predicates will not necessarily be the same as the theta-join criteria for finding candidate links above; in fact, the theta-join criteria is only an approximate metric for extracting potential candidate links, and the feature extraction should be as detailed as possible.

We use the following features to help DeepDive determine if an (entity, mention) pair should be linked:
- Exact string match
- Similarity score (described below) above a threshold
- Levenshtein edit distance below a threshold
- one is a substring of the other

The [similarity score](http://www.postgresql.org/docs/9.1/static/pgtrgm.html) is computed by counting the number ot trigrams that the two strings share.

For example, for the (e, m) pair with the text (Barack Obama, Barack Obama), all 4 features would be True and thus 4 tuples would be generated in the *link_feature* relation (one for each feature).


### 5. Inference

DeepDive models entity linking as a factor graph where:
- the variables are (entity, mention) pairs with corresponding True/False values, and
- the factors are features extracted between candidate entity-mention pairs.

The objective is to learn factor weights from training data and to infer values for all unknown variables.

The factors correspond to the following:
- Feature (e.g. edit distance, etc.)
- one-to-many constraint between entities and mentions


    feature: {
      input_query: """SELECT * FROM link_feature AS f INNER JOIN candidate_link AS c ON
        (f.link_id = c.id)"""
      function: "c.is_correct = Imply()"
      weight: "?(f.feature)"
    }

    single_mention_to_one_entity: {
      input_query: """SELECT * FROM 
          (SELECT * FROM candidate_link AS l1, candidate_link AS l2 
          WHERE l1.mid = l2.mid AND l1.eid <> l2.eid) AS t 
          INNER JOIN candidate_link AS c ON (t.l1.eid = c.eid AND t.l1.mid = c.mid)"""
      function: "c.is_correct = Imply()"
      weight: 10
    }

### 6. Evaluation

## Inspecting Probabilities and Weights
To evaluate DeepDive's performance on the KBP example we can first inspect the probabilites for the variable *candidate_link.is_correct*, and the learned weights. DeepDive creates a [view](http://en.wikipedia.org/wiki/View_(SQL)) called *inference_result_mapped_weights* in the database, which contains the weight names and the learned values sorted by absolute value.

DeepDive also generates a view called *candidate_link.is_correct_inference*, which contains our original data, augmented with the results of the inference step (probabilities).


### Calibration Plots
DeepDive provides a simple calibration utility to evaluate the performance of our example. It will evaluate the T/F values of the unknown variables as determined by the system and will compare those values against a holdout sample of the training set.

For the example, we wish to use 25% of the training set for calibration. We can specify this in application.conf:

    calibration.holdout_fraction: 0.25

DeepDive will produce a calibration plot in [LOCATION], which should look similar to the following:
// TODO



