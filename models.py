from abc import ABC, abstractmethod
from collections import defaultdict
import math
from document import Document
from math import log2, ceil

class RetrievalModel(ABC):
    @abstractmethod
    def document_to_representation(self, document: Document, stopword_filtering=False, stemming=False):
        raise NotImplementedError()

    @abstractmethod
    def query_to_representation(self, query: str):
        raise NotImplementedError()

    @abstractmethod
    def match(self, document_representation, query_representation) -> float:
        raise NotImplementedError()


class LinearBooleanModel(RetrievalModel):
    def __init__(self, documents: list[Document] = None):
        self.documents = documents if documents is not None else []

    def set_documents(self, documents: list[Document]):
        self.documents = documents

    def document_to_representation(self, document: Document, stopword_filtering=False, stemming=False):
        if stopword_filtering:
            return document.filtered_terms
        if stemming:
            return document.stemmed_terms
        return document.terms

    def query_to_representation(self, query: str):
        return query.lower().split()

    def match(self, document_representation, query_representation) -> float:
        return 1.0 if any(term in document_representation for term in query_representation) else 0.0

    def search(self, query: str) -> list:
        result = []
        query_representation = self.query_to_representation(query)
        for document in self.documents:
            document_representation = self.document_to_representation(document, stopword_filtering=True)
            if self.match(document_representation, query_representation):
                result.append(document.document_id)
        return result

    def __str__(self):
        return 'Boolean Model (Linear)'

class InvertedListBooleanModel(RetrievalModel):
    def __init__(self):
        self.inverted_index = {}

    def build_inverted_index(self, collection: list[Document], stopword_filtering=False, stemming=False):
        self.inverted_index = {}
        for document in collection:
            terms = self.document_to_representation(document, stopword_filtering, stemming)
            for term in terms:
                if term not in self.inverted_index:
                    self.inverted_index[term] = set()
                self.inverted_index[term].add(document.document_id)

    def document_to_representation(self, document: Document, stopword_filtering=False, stemming=False):
        if stopword_filtering:
            return document.filtered_terms
        if stemming:
            return document.stemmed_terms
        return document.terms

    def query_to_representation(self, query: str):
        return query.lower().split()

    def match(self, document_representation, query_representation) -> float:
        return 1.0 if any(term in document_representation for term in query_representation) else 0.0

    def __str__(self):
        return 'Boolean Model (Inverted List)'


class SignatureBasedBooleanModel(RetrievalModel):
    def __init__(self):
        self.signature_index = {}

    def build_signature_index(self, collection: list[Document], stopword_filtering=False, stemming=False):
        self.signature_index = {}
        for document in collection:
            terms = self.document_to_representation(document, stopword_filtering, stemming)
            signature = self.create_signature(terms)
            self.signature_index[document.document_id] = signature

    def document_to_representation(self, document: Document, stopword_filtering=False, stemming=False):
        if stopword_filtering:
            return document.filtered_terms
        if stemming:
            return document.stemmed_terms
        return document.terms

    def query_to_representation(self, query: str):
        return query.lower().split()

    def create_signature(self, terms: list[str]) -> int:
        signature = 0
        for term in terms:
            signature |= 1 << (hash(term) % 64)  # Using a 64-bit integer as the signature
        return signature

    def match(self, document_representation, query_representation) -> float:
        query_signature = self.create_signature(query_representation)
        return 1.0 if query_signature & document_representation == query_signature else 0.0

    def search(self, query: str, stopword_filtering=False, stemming=False) -> list:
        query_representation = self.query_to_representation(query)
        query_signature = self.create_signature(query_representation)
        results = []

        for doc_id, doc_signature in self.signature_index.items():
            if query_signature & doc_signature == query_signature:
                results.append(doc_id)
        return results

    def __str__(self):
        return 'Boolean Model (Signatures)'
    

class VectorSpaceModel(RetrievalModel):
    def __init__(self):
        self.inverted_index = defaultdict(list)
        self.document_lengths = {}

    def build_inverted_index(self, documents: list[Document]):
        document_frequency = defaultdict(int)

        for document in documents:
            term_count = defaultdict(int)
            for term in document.terms:
                term_count[term] += 1
            document_id = document.document_id
            self.document_lengths[document_id] = 0
            for term, count in term_count.items():
                tf = 1 + math.log10(count)
                self.inverted_index[term].append((document_id, tf))
                document_frequency[term] += 1

        num_documents = len(documents)
        for term, postings in self.inverted_index.items():
            idf = math.log10(num_documents / document_frequency[term])
            for i, (doc_id, tf) in enumerate(postings):
                tf_idf = tf * idf
                self.inverted_index[term][i] = (doc_id, tf_idf)
                self.document_lengths[doc_id] += tf_idf ** 2

        for doc_id in self.document_lengths:
            self.document_lengths[doc_id] = math.sqrt(self.document_lengths[doc_id])

    def document_to_representation(self, document: Document, stopword_filtering=False, stemming=False):
        pass

    def query_to_representation(self, query: str):
        return query.lower().split()

    def query_to_vector(self, query: str):
        term_count = defaultdict(int)
        for term in self.query_to_representation(query):
            term_count[term] += 1

        num_query_terms = len(term_count)
        query_vector = {}
        for term, count in term_count.items():
            tf = 1 + math.log10(count)
            idf = math.log10((num_query_terms + 1) / (term_count[term] + 1))
            query_vector[term] = tf * idf
        return query_vector

    def match(self, document_representation, query_representation) -> float:
        return 1.0 if any(term in document_representation for term in query_representation) else 0.0

    def __str__(self):
        return 'Vector Space Model'
