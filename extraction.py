import json
import re
from document import Document
from cleanup import remove_symbols

def extract_collection(source_file_path: str) -> list[Document]:
    """
    Loads a text file (aesopa10.txt) and extracts each of the listed fables/stories from the file.
    :param source_file_name: File name of the file that contains the fables
    :return: List of Document objects
    """
    catalog = [] 

    with open(source_file_path, 'r') as file:
        content = file.readlines()

    
    totalLines = len(content)
    lines_fableStart = []
    for i in range(0, totalLines-1):
    
        if(content[i] == '\n' and content[i+1] == '\n' and content[i+2] == '\n'):

            if(content[i+4] == '\n' and content[i+5] == '\n'):

                if(re.search('(?:\s?)[a-zA-Z]{1}\n', content[i+3])):

                    lines_fableStart.append(i+3)
        else:
            continue


    for i,fable in enumerate(lines_fableStart):
        if(i == len(lines_fableStart)-1):
           fable = content[lines_fableStart[i]:]
        else:
            fable = content[lines_fableStart[i]:lines_fableStart[i+1]]

        fable_title = fable[0].strip()
        fable_content = ' '.join(fable[3:]).replace('\n', ' ').strip()
        fable_content = remove_symbols(fable_content)
        fable_terms =  fable_content.split()  # simple tokenization, adjust as needed
        document = Document()
        document.document_id = i
        document.title = fable_title
        document.raw_text = fable_content
        document.terms = fable_terms
        catalog.append(document)



    return catalog

def save_collection_as_json(collection: list[Document], file_path: str) -> None:
    """
    Saves the collection to a JSON file.
    :param collection: The collection to store (= a list of Document objects)
    :param file_path: Path of the JSON file
    """

    serializable_collection = []
    for document in collection:
        serializable_collection += [{
            'document_id': document.document_id,
            'title': document.title,
            'raw_text': document.raw_text,
            'terms': document.terms,
            'filtered_terms': document.filtered_terms,
            'stemmed_terms': document.stemmed_terms
        }]

    with open(file_path, "w") as json_file:
        json.dump(serializable_collection, json_file)

def load_collection_from_json(file_path: str) -> list[Document]:
    """
    Loads the collection from a JSON file.
    :param file_path: Path of the JSON file
    :return: list of Document objects
    """
    try:
        with open(file_path, "r") as json_file:
            json_collection = json.load(json_file)

        collection = []
        for doc_dict in json_collection:
            document = Document()
            document.document_id = doc_dict.get('document_id')
            document.title = doc_dict.get('title')
            document.raw_text = doc_dict.get('raw_text')
            document.terms = doc_dict.get('terms')
            document.filtered_terms = doc_dict.get('filtered_terms')
            document.stemmed_terms = doc_dict.get('stemmed_terms')
            collection += [document]

        return collection
    except FileNotFoundError:
        print('No collection was found. Creating empty one.')
        return []
