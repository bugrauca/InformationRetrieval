import re
from document import Document

def get_measure(term: str) -> int:
    """
    Returns the measure m of a given term [C](VC){m}[V].
    :param term: Given term/word
    :return: Measure value m
    """
    form = re.sub(r'[^aeiouy]+', 'C', term)
    form = re.sub(r'[aeiouy]+', 'V', form)
    return form.count('VC')

def condition_v(stem: str) -> bool:
    """
    Returns whether condition *v* is true for a given stem (= the stem contains a vowel).
    :param stem: Word stem to check
    :return: True if the condition *v* holds
    """
    return bool(re.search(r'[aeiouy]', stem))

def condition_d(stem: str) -> bool:
    """
    Returns whether condition *d is true for a given stem (= the stem ends with a double consonant (e.g. -TT, -SS)).
    :param stem: Word stem to check
    :return: True if the condition *d holds
    """
    return len(stem) >= 2 and stem[-1] == stem[-2] and stem[-1] not in 'aeiou'

def cond_o(stem: str) -> bool:
    """
    Returns whether condition *o is true for a given stem (= the stem ends cvc, where the second c is not W, X or Y
    (e.g. -WIL, -HOP)).
    :param stem: Word stem to check
    :return: True if the condition *o holds
    """
    return len(stem) >= 3 and stem[-3] not in 'aeiou' and stem[-2] in 'aeiou' and stem[-1] not in 'aeiouwx'

def stem_term(term: str) -> str:
    """
    Stems a given term of the English language using the Porter stemming algorithm.
    :param term:
    :return:
    """
    original_term = term


    if term.endswith('sses'):
        term = term[:-4] + 'ss'
    elif term.endswith('ies'):
        term = term[:-3] + 'i'
    elif term.endswith('ss'):
        term = term
    elif term.endswith('s'):
        term = term[:-1]


    if term.endswith('eed'):
        if get_measure(term[:-3]) > 0:
            term = term[:-1]
    elif term.endswith('ed'):
        base = term[:-2]
        if condition_v(base):
            term = base
            if term.endswith('at') or term.endswith('bl') or term.endswith('iz'):
                term += 'e'
            elif condition_d(term) and not term.endswith(('l', 's', 'z')):
                term = term[:-1]
            elif get_measure(term) == 1 and cond_o(term):
                term += 'e'
    elif term.endswith('ing'):
        base = term[:-3]
        if condition_v(base):
            term = base
            if term.endswith('at') or term.endswith('bl') or term.endswith('iz'):
                term += 'e'
            elif condition_d(term) and not term.endswith(('l', 's', 'z')):
                term = term[:-1]
            elif get_measure(term) == 1 and cond_o(term):
                term += 'e'

 
    if term.endswith('y'):
        base = term[:-1]
        if condition_v(base):
            term = base + 'i'


    step2_suffixes = {
        'ational': 'ate', 'tional': 'tion', 'enci': 'ence', 'anci': 'ance', 'izer': 'ize', 'abli': 'able', 'alli': 'al',
        'entli': 'ent', 'eli': 'e', 'ousli': 'ous', 'ization': 'ize', 'ation': 'ate', 'ator': 'ate', 'alism': 'al',
        'iveness': 'ive', 'fulness': 'ful', 'ousness': 'ous', 'aliti': 'al', 'iviti': 'ive', 'biliti': 'ble'
    }
    for suffix, replacement in step2_suffixes.items():
        if term.endswith(suffix):
            base = term[:-len(suffix)]
            if get_measure(base) > 0:
                term = base + replacement
            break

 
    step3_suffixes = {
        'icate': 'ic', 'ative': '', 'alize': 'al', 'iciti': 'ic', 'ical': 'ic', 'ful': '', 'ness': ''
    }
    for suffix, replacement in step3_suffixes.items():
        if term.endswith(suffix):
            base = term[:-len(suffix)]
            if get_measure(base) > 0:
                term = base + replacement
            break

 
    step4_suffixes = [
        'al', 'ance', 'ence', 'er', 'ic', 'able', 'ible', 'ant', 'ement', 'ment', 'ent', 'ion', 'ou', 'ism', 'ate', 'iti',
        'ous', 'ive', 'ize'
    ]
    for suffix in step4_suffixes:
        if term.endswith(suffix):
            base = term[:-len(suffix)]
            if get_measure(base) > 1:
                term = base
            elif suffix == 'ion' and base.endswith(('s', 't')):
                term = base
            break


    if term.endswith('e'):
        base = term[:-1]
        if get_measure(base) > 1 or (get_measure(base) == 1 and not cond_o(base)):
            term = base


    if condition_d(term) and get_measure(term) > 1 and term.endswith('l'):
        term = term[:-1]

    return term

def stem_all_documents(collection: list[Document]):
    """
    For each document in the given collection, this method uses the stem_term() function on all terms in its term list.
    Warning: The result is NOT saved in the document's term list, but in the extra field stemmed_terms!
    :param collection: Document collection to process
    """
    for document in collection:
        document.stemmed_terms = [stem_term(term) for term in document.terms]

def stem_query_terms(query: str) -> str:
    """
    Stems all terms in the provided query string.
    :param query: User query, may contain Boolean operators and spaces.
    :return: Query with stemmed terms
    """
    terms = query.split()
    stemmed_terms = [stem_term(term) for term in terms]
    return ' '.join(stemmed_terms)
