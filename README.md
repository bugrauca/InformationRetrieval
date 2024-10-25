# Information Retrieval System

This project is an Information Retrieval (IR) System implemented in Python. It is designed to perform document indexing, preprocessing, retrieval, and evaluation using various IR models and techniques. Key features include Boolean retrieval, Vector Space Model with tf-idf weighting, stemming, stop word removal, and precision/recall evaluation.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Modules](#modules)
- [Examples](#examples)

## Overview
This IR system supports document preparation, search, and evaluation, implementing both Boolean retrieval and a Vector Space Model. Key components include stop word removal, stemming using the Porter algorithm, and the construction of an inverted list. Additionally, precision and recall are evaluated for the retrieval models.

## Features
- **Document Preparation**: Includes text preprocessing steps like tokenization, stop word removal, and stemming.
- **Boolean Retrieval**: Uses inverted lists for efficient Boolean searches.
- **Vector Space Model**: Implements tf-idf term weighting and cosine similarity for ranking results.
- **Precision and Recall Evaluation**: Assesses the effectiveness of the Boolean and Vector Space models.
- **Signature Implementation**: Optimized Boolean search using signatures.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ir-system.git
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
Run the `ir_system.py` script to start the IR system:
```bash
python ir_system.py
```

## Modules
The project is modularized into several files, each with a specific role:

### `document.py`
Handles document preparation, including tokenization, stop word removal, and text normalization.

### `extraction.py`
Responsible for extracting relevant terms and generating term-document matrices.

### `porter.py`
Contains the implementation of the Porter Stemmer algorithm to reduce terms to their root forms.

### `models.py`
Implements the Boolean and Vector Space models, including tf-idf weighting and cosine similarity for scoring.

### `ir_system.py`
The main driver script that orchestrates the various components of the IR system, handling user input and calling the appropriate functions.

### `cleanup.py`
Assists with text cleaning and pre-processing tasks such as punctuation removal, lowercasing, and basic tokenization.

## Examples
Here’s how you can use the system for a Boolean query:

```python
# Example Boolean query
query = "information AND retrieval"
results = BooleanModel.search(query)
print("Search Results:", results)
```

And for Vector Space Model retrieval with tf-idf weighting:

```python
# Example Vector Space Model query
query = "machine learning applications"
results = VectorSpaceModel.search(query)
print("Ranked Search Results:", results)
```
