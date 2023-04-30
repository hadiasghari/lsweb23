# lsweb23

This repository consists of a number of Python notebooks and scripts for detecting __Leichte Sprache__ on the web. 
It is a companion of the following paper:

> H. Asghari, F. Hewett, & T. Züger. (2023). "On the Prevalence of Leichte Sprache on the German Web". In _Proceedings of WebSci ’23._ https://doi.org/10.1145/3578503.3583599 

The included notebooks and scripts are as follows:

- ___1.training-neural-classifier.ipynb___:  training notebook for the easy vs. standard German classifier 
- ___2A.create-our-curlie-set.ipynb___: notebook to create curated curlie dataset
- ___2B.create-oscar-subset.ipynb___: notebook to create subset of Oscar22 domains that are within Curlie and end with .de
- ___3.classify-oscar-pages.py___: script which applies the classifier to the Oscar subset
- ___4.LS-crawler___: Scrapy-based crawler to save LeichteSprache pages found on a list of websites
- ___5.paper-analysis.ipynb___: notebook to replicate our paper's analysis 

The following files are additionally included:

- ___mbow-alldata___: classifier model trained on our full dataset (output of step 1)
- ___dataset-xxx-open.csv___:  part of the test & train data used to train the classifier (about a quarter of the data that we can share publicly) 
- ___curlie-ourset.csv___: our subset of Curlie domains with flattened categories (output of step 2A)
- ___oscar22-classified.csv.xz___: a very large file containing our Oscar22 subset URLs passed through our classifier (output of step 3)

If you have any questions or notice any errors, please feel free to open an issue or contact the authors.

The repository code is licensed under the Mozilla Public License 2.0. If you make use of it, please consider citing our paper. 
