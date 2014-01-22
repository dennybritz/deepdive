---
layout: default
---

# Overview

To illustrate a more concrete application of DeepDive, we provide a simple entity-linking example, located in examples/kbp. This example is taken from the [KBP entity linking competition](http://www.nist.gov/tac/2013/KBP/EntityLinking/). The objective of the competition is to extract instances (mentions) of the type PERSON, ORGANIZATION, or GPE (geo-political entity) from a text data corpus, and to link these mentions to known Wikipedia entries (entities).

For illustrative purposes, we will extract PERSON mentions from a corpus of news articles (the processed data is in data/mention/mentions.csv) and link them to PERSON entities (a database table of these entities is in data/entity/entity.sql).

Since our objective is to figure out whether a given (entity, mention) pair should be linked, the inference variable is the column *is_correct* in the *candidate_link()* table. To perform linking, a training set is used to learn the association between possible (entity, mention) pairs. DeepDive uses the known (entity, mention) links to infer associations between unknown links. 

DeepDive extracts features from the entity and mention text, and then performs probabilistic inference on the (entity, mention) variables.

At a high level, the following tasks are performed:
1. Data loading
2. Candidate link extraction
3. Adding positive and negative examples
4. Feature extraction
5. Inference
6. Evaluation


### Dependencies

In addition to the DeepDive dependencies, you will need the following libraries to run this example (both used to extract text features in udf/extract_features.py):
* [NLTK](http://nltk.org/)
* [Python-ngram](https://code.google.com/p/python-ngram/) 


### 1. Data Loading

(see data/README.txt)

The script prepare_data.sh creates and populates the necessary tables from the provided SQL and CSV files.


### 2. Candidate Link Extraction

To begin the process of inferring whether or not a particular (entity, mention) pair should be linked, we must first arrive at a list of candidate (entity, mention) pairs that will be used as input to the feature extraction step. A good initial guess for this would be all possible (entity, mention) pairs, given all the mentions and entities in our input data. However, the number of such pairs scales poorly with data set size and this approach is impractical. Thus, to extract candidate pairs, we perform a theta join on the mention and entity tables (comparing the text_contents fields), as illustrated by this query:

```
SELECT * FROM mention INNER JOIN entity ON
      (lower(mention.text_contents) = lower(entity.text_contents) OR
      levenshtein(lower(mention.text_contents), lower(entity.text_contents)) < 3 OR
      similarity(lower(mention.text_contents), lower(entity.text_contents)) >= 0.75) OR
      position(lower(mention.text_contents), lower(entity.text_contents)) >= 0 OR
      position(lower(entity.text_contents), lower(mention.text_contents))

```

An entry in the *candidate_link* table is created if there exists a (mention, entity) pair such that any of the following conditions hold:
- their lowercase text matches exactly
- their [Levenshtein distance](http://en.wikipedia.org/wiki/Levenshtein_distance) is less than 3
- their similarity score (explaine below) is at least 0.75
- one is a substring of the other

We want to predict whether the "Barack Obama" mention should link to the "Barack Obama" entity. First, we find potential candidate matches between entities and mentions. What qualifies as a candidate match will depend on metrics that tells us how similar the entity and mention in an (e, m) pair are. For a given metric we want a binary output indicating whether the pair is a candidate match.

Candidate (entity, mention) pairs are found by performing a theta join on the entity and mention tables, using the text attributes as inputs to the predicate. The example uses the following predicates, implemented in SQL:
- Exact string match
- Similarity score above a threshold of 0.75
- Levenshtein edit distance below 3

Candidate (e, m) tuples must be distinct, so after populating the candidate table a view is created to extract the unique (e, m) pairs from all candidates. 

### 3. Feature extraction

Once the candidate (entity, mention) pairs are found, feature extraction is performed for each candidate (e, m) pair. Features are binary indicators of whether certain predicates are true. The output of this step is the link_features relation: link_feature(entity_id, mention_id, feature_type) where feature_type is a string name representing a particular feature (e.g. exact_string_match). 

 The example uses the following features:
- Exact string match
- Similarity score above a threshold of 0.75
- Levenshtein edit distance below 3

Note that the features are the same as the predicates that are used to determine if a pair is a candidate link or not.

For example, for the (e, m) pair with the text (Barack Obama, Barack Obama), all 3 features would be True and thus 3 tuples would be generated in the link_feature relation: (e, m, 'exact_string_match'), (e, m, 'similarity_above_threshold', 'levenshtein_distance_below_3').

```
[insert extractor code from application.conf with explanation]
```

### 4. Inference

DeepDive models entity linking as a factor graph where the variables are (entity, mention) pairs with corresponding True/False values, factors are features extracted between candidate entity-mention pairs, and the objective is to learn factor weights from training data and infer values for all uknown variables in the query data.

As outlined in application.conf, our variables are unique (entity, mention) pairs such that a given mention only links to one entity.

The factors are as follows:
- Feature type (e.g. edit distance, etc.)
- 1-to-many constraint between entities and mentions

```
[code snippet]
```

### 5. Evaluation

## Inspecting Probabilities and Weights
To evaluate DeepDive's performance on the example we can first inspect the probabilites for the variable link_feature.is_correct, and the learned weights. DeepDive creates a view called inference_result_mapped_weights in the database, which contains the weight names and the learned values sorted by absolute value.

DeepDive also generates a view called link_feature.is_correct_inference, which contains our original data, augmented with the results of the inference step (probabilities).


## Calibration Plots
DeepDive provides a simple calibration utility to evaluate the performance of our example. It will evaluate the T/F values of the unknown variables as determined by the system and will compare those values against a holdout sample of the training set.

For the example, we wish to use 25% of the training set for calibration. We can specify this in application.conf:

```
calibration.holdout_fraction: 0.25
```

The system will generate a single calibration file for the link_feature.is_correct variable (in target/calibration/link_feature.is_correct.tsv). The structure of this file is explained on the [calibration](calibration.html) page.

To generate a plot from the calibration file, simply run the script helper_scripts/calibrate.sh: it will place a calibration plot in the output/ directory.


