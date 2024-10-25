from document import Document
import string
from collections import Counter

def remove_symbols(text_string: str) -> str:
    """
    Removes all punctuation marks and similar symbols from a given string.
    Occurrences of "'s" are removed as well.
    :param text:
    :return:
    """
    text_string = text_string.lower()
    text_string = text_string.replace("'s", "")
    text_string = text_string.translate(str.maketrans('', '', string.punctuation))
    return text_string

def is_stop_word(term: str, stop_word_list: list[str]) -> bool:
    """
    Checks if a given term is a stop word.
    :param stop_word_list: List of all considered stop words.
    :param term: The term to be checked.
    :return: True if the term is a stop word.
    """
    return term in stop_word_list

def remove_stop_words_from_term_list(term_list: list[str], stop_word_list: list[str]) -> list[str]:
    """
    Takes a list of terms and removes all terms that are stop words.
    :param term_list: List that contains the terms
    :param stop_word_list: List of stop words.
    :return: List of terms without stop words
    """
    cleaned_term_list = [remove_symbols(term) for term in term_list]
    filtered_terms = [term for term in cleaned_term_list if not is_stop_word(term, stop_word_list)]
    return filtered_terms

def filter_collection(collection: list[Document], stop_word_list: list[str]):
    """
    For each document in the given collection, this method takes the term list and filters out the stop words.
    Warning: The result is NOT saved in the documents term list, but in an extra field called filtered_terms.
    :param collection: Document collection to process
    """
    for document in collection:
        document.filtered_terms = remove_stop_words_from_term_list(document.terms, stop_word_list)
    return collection

def load_stop_word_list(raw_file_path: str) -> list[str]:
    """
    Loads a text file that contains stop words and saves it as a list. The text file is expected to be formatted so that
    each stop word is in a new line, e. g. like englishST.txt
    :param raw_file_path: Path to the text file that contains the stop words
    :return: List of stop words
    """
    with open(raw_file_path, 'r') as file:
        stop_words = [line.strip().lower() for line in file]
    return stop_words

def create_stop_word_list_by_frequency(collection: list[Document]) -> list[str]:
    """
    Uses the method of J. C. Crouch (1990) to generate a stop word list by finding high and low frequency terms in the
    provided collection.
    :param collection: Collection to process
    :return: List of stop words
    """
    term_counter = Counter()
    for document in collection:
        term_counter.update(document.terms)
    
    total_terms = sum(term_counter.values())
    high_freq_threshold = total_terms * 0.01
    low_freq_threshold = 2
    
    stop_words = [term for term, freq in term_counter.items() if freq > high_freq_threshold or freq <= low_freq_threshold]
    return stop_words
