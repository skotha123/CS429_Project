# indexer.py
import numpy as np
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from gensim.models import Word2Vec
import faiss
from collections import defaultdict
import os


class TextIndexer:
    def __init__(self, documents):
        self.documents = documents
        self.tfidf_vectorizer = TfidfVectorizer()
        self.word2vec_model = None
        self.tfidf_matrix = None
        self.index = None

    def build_tfidf_index(self):
        # Build the TF-IDF representation
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.documents)

    def build_word2vec_model(self, size=100, window=5, min_count=1, workers=4):
        # Tokenize the documents
        tokenized_docs = [doc.split() for doc in self.documents]
        # Build the Word2Vec model
        self.word2vec_model = Word2Vec(tokenized_docs, vector_size=size, window=window, min_count=min_count, workers=workers)

    def build_faiss_index(self):
        # Creating a matrix of vectors for the index
        # We average Word2Vec vectors of all words in the document to create a document vector
        doc_vectors = []
        for doc in self.documents:
            words = doc.split()
            vectors = [self.word2vec_model.wv[word] for word in words if word in self.word2vec_model.wv]
            if vectors:
                doc_vectors.append(np.mean(vectors, axis=0))
            else:
                doc_vectors.append(np.zeros(self.word2vec_model.vector_size))  # Empty vector for docs with no words in vocab
        doc_vectors = np.array(doc_vectors)

        # Build and train the FAISS index
        self.index = faiss.IndexFlatL2(self.word2vec_model.vector_size)
        self.index.add(doc_vectors)

    def save_index(self, file_name):
        # Save the index to a file
        with open(file_name, 'wb') as f:
            pickle.dump((self.tfidf_vectorizer, self.tfidf_matrix, self.word2vec_model, self.index), f)

    def load_index(self, file_name):
        # Load the index from a file
        with open(file_name, 'rb') as f:
            self.tfidf_vectorizer, self.tfidf_matrix, self.word2vec_model, self.index = pickle.load(f)



def load_documents_from_file(file_path):
    documents = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            current_document = []
            for line in file:
                if line.startswith('URL:'):
                    if current_document:  # Save the previous document
                        documents.append(' '.join(current_document))
                        current_document = []
                else:
                    current_document.append(line.strip())
            if current_document:  # Make sure to add the last document
                documents.append(' '.join(current_document))
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
    return documents

file_path = 'wikipedia_ai.txt'
documents = load_documents_from_file(file_path)

if documents:  # Ensure there is data to process
    indexer = TextIndexer(documents)
    indexer.build_tfidf_index()
    indexer.build_word2vec_model()
    indexer.build_faiss_index()
    indexer.save_index('index.pkl')  # Saving the index

    # Optionally, to load and use the index:
    indexer.load_index('index.pkl')
else:
    print("No documents were loaded from the file.")
