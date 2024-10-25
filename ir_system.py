import json
import os
import time
import cleanup
import extraction
import models
import porter
from document import Document


RAW_DATA_PATH = "raw_data"
DATA_PATH = "data"
COLLECTION_PATH = os.path.join(DATA_PATH, "my_collection.json")
STOPWORD_FILE_PATH = os.path.join(DATA_PATH, "stopwords.json")

(
    CHOICE_LIST,
    CHOICE_SEARCH,
    CHOICE_EXTRACT,
    CHOICE_UPDATE_STOP_WORDS,
    CHOICE_SET_MODEL,
    CHOICE_SHOW_DOCUMENT,
    CHOICE_EXIT,
) = (1, 2, 3, 4, 5, 6, 9)
MODEL_BOOL_LIN, MODEL_BOOL_INV, MODEL_SIG, MODEL_VSM_INV = 1, 2, 3, 4
SW_METHOD_LIST, SW_METHOD_CROUCH = 1, 2


class InformationRetrievalSystem(object):
    def __init__(self):
        if not os.path.isdir(DATA_PATH):
            os.makedirs(DATA_PATH)

        try:
            self.collection = extraction.load_collection_from_json(COLLECTION_PATH)
        except FileNotFoundError:
            print("No previous collection was found. Creating empty one.")
            self.collection = []

        try:
            with open(STOPWORD_FILE_PATH, "r") as f:
                self.stop_word_list = json.load(f)
        except FileNotFoundError:
            print("No stopword list was found.")
            self.stop_word_list = []

        self.model = None
        self.output_k = 5

    def main_menu(self):
        while True:
            print(f"Current retrieval model: {self.model}")
            print(f"Current collection: {len(self.collection)} documents")
            print()
            print("Please choose an option:")
            print(f"{CHOICE_LIST} - List documents")
            print(f"{CHOICE_SEARCH} - Search for term")
            print(f"{CHOICE_EXTRACT} - Build collection")
            print(f"{CHOICE_UPDATE_STOP_WORDS} - Rebuild stopword list")
            print(f"{CHOICE_SET_MODEL} - Set model")
            print(f"{CHOICE_SHOW_DOCUMENT} - Show a specific document")
            print(f"{CHOICE_EXIT} - Exit")

            try:
                action_choice = int(input("Enter choice: "))
            except ValueError:
                print(
                    "Invalid choice. Please enter a number corresponding to the options."
                )
                continue

            if action_choice == CHOICE_LIST:
                if self.collection:
                    for document in self.collection:
                        print(document)
                else:
                    print("No documents.")
                print()

            elif action_choice == CHOICE_SEARCH:
                if self.model is None:
                    print("Please set a retrieval model before searching.")
                    continue

                SEARCH_NORMAL, SEARCH_SW, SEARCH_STEM, SEARCH_SW_STEM = 1, 2, 3, 4
                print("Search options:")
                print(f"{SEARCH_NORMAL} - Standard search (default)")
                print(f"{SEARCH_SW} - Search documents with removed stopwords")
                print(f"{SEARCH_STEM} - Search documents with stemmed terms")
                print(
                    f"{SEARCH_SW_STEM} - Search documents with removed stopwords AND stemmed terms"
                )
                try:
                    search_mode = int(input("Enter choice: "))
                except ValueError:
                    print(
                        "Invalid choice. Please enter a number corresponding to the options."
                    )
                    continue

                stop_word_filtering = (search_mode == SEARCH_SW) or (
                    search_mode == SEARCH_SW_STEM
                )
                stemming = (search_mode == SEARCH_STEM) or (
                    search_mode == SEARCH_SW_STEM
                )

                query = input("Query: ")
                if stemming:
                    query = porter.stem_query_terms(query)

                st = time.time()
                if isinstance(self.model, models.InvertedListBooleanModel):
                    results = self.inverted_list_search(
                        query, stemming, stop_word_filtering
                    )
                elif isinstance(self.model, models.SignatureBasedBooleanModel):
                    results = self.model.search(query, stop_word_filtering, stemming)
                    results = [
                        (1.0, self.get_document_by_id(doc_id)) for doc_id in results
                    ]
                elif isinstance(self.model, models.VectorSpaceModel):
                    results = self.vsm_search(query)
                else:
                    results = self.basic_query_search(
                        query, stemming, stop_word_filtering
                    )
                et = time.time()

                results = [result for result in results if result[0] > 0]

                for score, document in results:
                    print(f"{score}: {document}")

                print()
                print(f"precision: {self.calculate_precision(results):.2f}")
                print(f"recall: {self.calculate_recall(results):.2f}")
                print(f"Time taken: {(et - st) * 1000:.2f} ms")

            elif action_choice == CHOICE_EXTRACT:
                raw_collection_file = os.path.join(RAW_DATA_PATH, "aesopa10.txt")
                self.collection = extraction.extract_collection(raw_collection_file)
                assert isinstance(self.collection, list)
                assert all(isinstance(d, Document) for d in self.collection)

                if input("Should stopwords be filtered? [Y/N]: ") == "y":
                    self.collection = cleanup.filter_collection(
                        self.collection, self.stop_word_list
                    )

                if input("Should stemming be performed? [Y/N]: ") == "y":
                    porter.stem_all_documents(self.collection)

                extraction.save_collection_as_json(self.collection, COLLECTION_PATH)
                print("Done.\n")

            elif action_choice == CHOICE_UPDATE_STOP_WORDS:
                print("Available options:")
                print(f"{SW_METHOD_LIST} - Load stopword list from file")
                print(
                    f"{SW_METHOD_CROUCH} - Generate stopword list using Crouch's method"
                )

                try:
                    method_choice = int(input("Enter choice: "))
                except ValueError:
                    print(
                        "Invalid choice. Please enter a number corresponding to the options."
                    )
                    continue

                if method_choice in (SW_METHOD_LIST, SW_METHOD_CROUCH):
                    if method_choice == SW_METHOD_LIST:
                        self.stop_word_list = cleanup.load_stop_word_list(
                            os.path.join(RAW_DATA_PATH, "englishST.txt")
                        )
                        print("Done.\n")
                    elif method_choice == SW_METHOD_CROUCH:
                        self.stop_word_list = (
                            cleanup.create_stop_word_list_by_frequency(self.collection)
                        )
                        print("Done.\n")

                    with open(STOPWORD_FILE_PATH, "w") as f:
                        json.dump(self.stop_word_list, f)
                else:
                    print("Invalid choice.")

            elif action_choice == CHOICE_SET_MODEL:
                print()
                print("Available models:")
                print(f"{MODEL_BOOL_LIN} - Boolean model with linear search")
                print(f"{MODEL_BOOL_INV} - Boolean model with inverted lists")
                print(f"{MODEL_SIG} - Signature Based Boolean Model")
                print(f"{MODEL_VSM_INV} - Vector Space Model with inverted lists")

                try:
                    model_choice = int(input("Enter choice: "))
                except ValueError:
                    print(
                        "Invalid choice. Please enter a number corresponding to the options."
                    )
                    continue

                if model_choice == MODEL_BOOL_LIN:
                    self.model = models.LinearBooleanModel()
                elif model_choice == MODEL_BOOL_INV:
                    self.model = models.InvertedListBooleanModel()
                    self.model.build_inverted_index(self.collection, stopword_filtering=True, stemming=True)
                elif model_choice == MODEL_SIG:
                    self.model = models.SignatureBasedBooleanModel()
                    self.model.build_signature_index(
                        self.collection, stopword_filtering=True, stemming=True
                    )
                elif model_choice == MODEL_VSM_INV:
                    self.model = models.VectorSpaceModel()
                else:
                    print("Invalid choice.")

            elif action_choice == CHOICE_SHOW_DOCUMENT:
                try:
                    target_id = int(input("ID of the desired document: "))
                except ValueError:
                    print("Invalid choice. Please enter a valid document ID.")
                    continue
                
                found = False
                for document in self.collection:
                    if document.document_id == target_id:
                        print(document.title)
                        print("-" * len(document.title))
                        print(document.raw_text)
                        found = True

                if not found:
                    print(f"Document #{target_id} not found!")

            elif action_choice == CHOICE_EXIT:
                break
            else:
                print("Invalid choice.")

            print()
            input("Press ENTER to continue...")
            print()

    def basic_query_search(self, query: str, stemming: bool, stop_word_filtering: bool) -> list:
        query_representation = self.model.query_to_representation(query)
        document_representations = [self.model.document_to_representation(d, stop_word_filtering, stemming)
                                    for d in self.collection]
        scores = [self.model.match(dr, query_representation) for dr in document_representations]
        ranked_collection = sorted(zip(scores, self.collection), key=lambda x: x[0], reverse=True)
        results = ranked_collection[: self.output_k]
        return results

    def inverted_list_search(self, query: str, stemming: bool, stop_word_filtering: bool) -> list:
        if not isinstance(self.model, models.InvertedListBooleanModel):
            raise TypeError("Model is not an InvertedListBooleanModel")

        if not self.model.inverted_index:
            self.model.build_inverted_index(
                self.collection, stop_word_filtering, stemming
            )

        query_representation = self.model.query_to_representation(query)
        results = set()
        for term in query_representation:
            if term in self.model.inverted_index:
                results.update(self.model.inverted_index[term])

        ranked_collection = [
            (1.0, doc) for doc in self.collection if doc.document_id in results
        ]
        return ranked_collection

    def calculate_precision(self, result_list: list[tuple]) -> float:
        try:
            with open(os.path.join(RAW_DATA_PATH, "ground_truth.txt"), "r") as f:
                ground_truth = []
                for line in f:
                    if line.strip() and not line.startswith(
                        "#"
                    ):  # Skip empty lines and comments
                        parts = line.strip().split("-")
                        if len(parts) > 1:
                            ids = parts[1].split(",")
                            ground_truth.extend([int(doc_id.strip()) for doc_id in ids])
                        else:
                            ground_truth.append(int(line.strip()))
        except FileNotFoundError:
            print("Ground truth file not found.")
            return 0.0

        retrieved_docs = [doc.document_id for score, doc in result_list]
        relevant_docs = set(ground_truth)
        true_positives = len(
            [doc_id for doc_id in retrieved_docs if doc_id in relevant_docs]
        )

        return round(true_positives / len(retrieved_docs), 2) if retrieved_docs else 0.0

    def calculate_recall(self, result_list: list[tuple]) -> float:
        try:
            with open(os.path.join(RAW_DATA_PATH, "ground_truth.txt"), "r") as f:
                ground_truth = []
                for line in f:
                    if line.strip() and not line.startswith(
                        "#"
                    ):  # Skip empty lines and comments
                        parts = line.strip().split("-")
                        if len(parts) > 1:
                            ids = parts[1].split(",")
                            ground_truth.extend([int(doc_id.strip()) for doc_id in ids])
                        else:
                            ground_truth.append(int(line.strip()))
        except FileNotFoundError:
            print("Ground truth file not found.")
            return 0.0

        retrieved_docs = [doc.document_id for score, doc in result_list]
        relevant_docs = set(ground_truth)
        true_positives = len([doc_id for doc_id in retrieved_docs if doc_id in relevant_docs])

        return round(true_positives / len(relevant_docs), 2) if relevant_docs else 0.0

    def get_document_by_id(self, doc_id):
        for document in self.collection:
            if document.document_id == doc_id:
                return document
        return None

    def vsm_search(self, query: str) -> list:
        if not isinstance(self.model, models.VectorSpaceModel):
            raise TypeError("Model is not a VectorSpaceModel")

        if not self.model.inverted_index:
            self.model.build_inverted_index(self.collection)

        query_vector = self.model.query_to_vector(query)
        scores = {}

        for term, weight in sorted(
            query_vector.items(), key=lambda item: item[1], reverse=True
        ):
            if term in self.model.inverted_index:
                for doc_id, term_weight in self.model.inverted_index[term]:
                    if doc_id not in scores:
                        scores[doc_id] = 0
                    scores[doc_id] += term_weight * weight

            if len(scores) > self.output_k:
                sorted_scores = sorted(scores.values(), reverse=True)
                threshold = sorted_scores[self.output_k - 1]
                if all(score < threshold for score in sorted_scores[self.output_k :]):
                    break

        ranked_collection = [
            (round(score, 2), doc)
            for doc_id, score in scores.items()
            for doc in self.collection
            if doc.document_id == doc_id
        ]
        ranked_collection.sort(reverse=True, key=lambda x: x[0])
        return ranked_collection[: self.output_k]


if __name__ == "__main__":
    InformationRetrievalSystem().main_menu()
    exit(0)
