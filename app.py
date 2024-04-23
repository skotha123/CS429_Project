from flask import Flask, request, jsonify
import nltk
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
from nltk import word_tokenize
from nltk.metrics.distance import edit_distance
import numpy as np
import pickle

# Ensure all necessary NLTK resources are downloaded
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')
nltk.download('stopwords') 

app = Flask(__name__)
#server.py
# Load the pre-constructed index
def load_index(file_name):
    with open(file_name, 'rb') as f:
        tfidf_vectorizer, tfidf_matrix, word2vec_model, faiss_index = pickle.load(f)
    return tfidf_vectorizer, word2vec_model, faiss_index

tfidf_vectorizer, word2vec_model, faiss_index = load_index('index.pkl')

# Load stopwords set
stop_words = set(stopwords.words('english'))

def correct_spelling(query):
    corrected_query = []
    for word in word_tokenize(query):
        if word.lower() not in stop_words:
            synsets = wn.synsets(word)
            if not synsets:
                # No synsets indicate potential misspelling
                suggestions = [lemma.name() for syn in wn.all_synsets() for lemma in syn.lemmas() if lemma.name()]
                if suggestions:
                    word = min(suggestions, key=lambda x: edit_distance(word, x))
            corrected_query.append(word)
    return ' '.join(corrected_query)

def expand_query(query):
    expanded_query = set()
    for word in word_tokenize(query):
        synsets = wn.synsets(word)
        for syn in synsets:
            for lemma in syn.lemmas():
                expanded_query.add(lemma.name().replace('_', ' '))
    return ' '.join(expanded_query)

@app.route('/query', methods=['POST'])
def process_query():
    data = request.json
    query = data.get('query', '')
    
    # Validate the query
    if not query:
        return jsonify({'error': 'Empty query'}), 400

    # Spell correction and query expansion
    corrected_query = correct_spelling(query)
    expanded_query = expand_query(corrected_query)

    # Convert query to vector and search in the FAISS index
    query_vector = np.mean([word2vec_model.wv[word] for word in corrected_query.split() if word in word2vec_model.wv], axis=0)
    distances, indices = faiss_index.search(np.array([query_vector]).astype('float32'), 5)  # Top-5 results

    results = {'corrected_query': corrected_query, 'expanded_query': expanded_query, 'distances': distances.tolist(), 'indices': indices.tolist()}
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
