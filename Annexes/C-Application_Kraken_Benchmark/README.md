# KRAKEN-BENCHMARK, <i>Fluid and Experimental metrics dashboard for HTR/OCR and NLP projects</i>

<img src="./KB-app/kb_report/static/KB_logo.png" alt="KB-logo" width="120px">
<img src="./Documentation-Research/inr_logo_grisbleu.png" alt="KB-logo" width="190px">

version 1.1.1

Kraken-Benchmark allows you to create a metrics dashboard to evaluate your machine learning transcription models. Kraken-Benchmark is used as a CLI which performs the calculations to display them in a web application that works with Flask. Kraken-Benchmark also relies on the [Kraken API](http://kraken.re) (PSL-eScripta) to perform the transcription of your images.

Most of the metrics use classic syntactic similarity algorithms and fuzzy string matching research; among these:

- Ratcliff / Obershelp algorithm
- Levenshtein & Levenshtein distance algorithm
- Word Error Rate, Character Error Rate, Word Accuracy
- Hamming distance

accompanied by visualizations:

- histogram of the operations of passing from a reference sentence to a predicted sentence
- confusion matrix of the most frequent pairs of character errors
- ranking of the most frequent pairs of character errors
- visualizations of sequences in the form of signals

Additionally, Kraken-Benchmark allows you to refine the parameters of your models with the interpretation of your results, to design an evaluation pipeline from the transcription of your text corpus to more ambitious NLP projects such as entity recognition named, segmentation, disambiguation, word-spotting etc.

This is why the application already integrates metrics such as:

- jaccard index
- cosine similarity (using TF-IDF vectors, bag of words metric)

This aspect should evolve with the integration of the [entity-fishing](http://cloud.science-miner.com/nerd/) API.

### Stack

Env : Anaconda

HTR/OCR system : Kraken API

Pre-processing text data : NLTK

Data Visualizations : Matplotlib, Seaborn, Pandas, Difflib

Metrics : STS Tools lib, Sklearn, Numpy, python-Levenshtein, Kraken API, Difflib

Web application : Flask

Research : Jupyter notebook

### Install

clone kraken-Benchmark repository :

**note : KB-app is currently the most updated branch**

```$ git clone https://gitlab.inria.fr/dh-projects/kraken-benchmark.git```

```$ cd KB-app/```

create a new conda env :

```$ conda env create --file environment.yml```

### Process

1. start a project :

```

├── KB-app/
│    ├── dataset_GT/   : contains your reference transcription files (ground truth set) 
│    ├── images/       : contains your images to HTR/OCR 
|    ├── model/        : contains your model (use CLI kraken to generate one)
|    ├── kraken_benchmark.py

```

- To do a test you can use the Jules Verne test set located ```sets_test/jules_verne_set_test```  (by default, this set is loaded in KB to test, you can modify it)

2. Rename your files, with labels, to match your ground truth and images, such as :
- filename_image_1.jpeg, filename_image_2.jpeg, filename_image_3.jpeg etc.
- filename_GT_1.txt, filename_GT_2.txt, filename_GT_3.txt etc.

### Usages 

```kraken_benchmark.py [-h] [--input INPUT] [--label] [--verbosity] [--clean_text]```

- Example of basic command line to launch program :

```$ python kraken_benchmark.py```

### Options

1. [input] Specify location of images, models and ground truth if
not in default location (default = current directory)

2. [label] Attach a metadata description on your each set's
image to display it in the HTML dashboard

3. [verbosity] View all the objects processed during the automatic transcription phase

4. [clean-text] Performs a few cleanning steps to remove
non-alphabetic characters, punctuation, numbers.
depends on the needs of the project. (in construction...)


