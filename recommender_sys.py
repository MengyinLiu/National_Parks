# -*- coding: utf-8 -*-
"""
Created June, 9th, 2017
@author: Mengyin Liu
"""

import pandas as pd
from gensim import models
import numpy as np
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.metrics.pairwise import cosine_similarity
import re
import pickle

def tokenizer(review):

    lmtzr = WordNetLemmatizer()
    letters_only = re.sub("[^a-zA-Z]", " ", review)
    tokenized_review = word_tokenize(letters_only.strip().lower())
    stop = stopwords.words('english')
    lemmatize_review = [lmtzr.lemmatize(w) for w in tokenized_review if w not in stop]

    return lemmatize_review


def get_vectors(word_list):
    feature_vectors = []
    for word in word_list:
        try:
            word_vec = model[word]
            feature_vectors.append(word_vec)
        except:
            pass

    return pd.DataFrame(zip(*feature_vectors)).mean(axis=1).tolist()


def get_park_vectors(place_name_list):
    vector_list = []
    for place in place_name_list:
        review_list = all_parks[(all_parks['Park Name'] == place.split(': ')[0]) & (all_parks['Things To Do'] == place.split(': ')[1])]['Review']
        word_list = []
        for review in review_list:
            word_list.extend(tokenizer(review))
        word_vector = get_vectors(word_list)
        vector_list.append(word_vector)

    return vector_list


def get_query_vector(query):
    lemmatize_query = tokenizer(query)
    query_vector = get_vectors(lemmatize_query)

    return query_vector


def get_vector_for_all_parks():
    place_name_list = (all_parks['Park Name'] + ': ' + all_parks['Things To Do']).unique()
    cleaned_place_name_list = [x for x in place_name_list if str(x) != 'nan']
    park_vector_list = get_park_vectors(cleaned_place_name_list)

    with open("new_vector.txt", "wb") as park_vector:
        pickle.dump(park_vector_list, park_vector)

    return


def cal_similarity(query_vector, park_vector):

    similarity = cosine_similarity(query_vector, park_vector)
    return similarity


def main():

    all_parks = pd.read_csv('/Users/mliu/National_Parks/park_data/all_parks.csv'
                            , usecols=[u'Park Name', u'Review', u'Review Date', u'Review Rating', u'Review Title', u'Things To Do']
                            , dtype={'Park Name': str, 'Review': str, 'Review Date': str, 'Review Ratings': float,
                                     'Review Title': str, 'Things To Do': str}
                            )

    all_parks.groupby(["Park Name", "Things To Do"]).size()

    model = models.KeyedVectors.load_word2vec_format(
        '/Users/mliu/National_Parks/data/GoogleNews-vectors-negative300.bin', binary=True)

    with open("new_vector.txt", "rb") as park_vector:
        park_vector_list = pickle.load(park_vector)

    place_name_list = (all_parks['Park Name'] + ': ' + all_parks['Things To Do']).unique()
    cleaned_place_name_list = [x for x in place_name_list if str(x) != 'nan']
    # query = raw_input("Describe the place you want to go: ")
    query = 'I want to go to places with great rain forest and clear lakes'
    query_vector = get_query_vector(query)
    # similarity_score = [cal_similarity(np.array(query_vector).reshape(1,-1), np.array(park_vector).reshape(1,-1)) for park_vector in park_vector_list]
    similarity_list = []
    for park_vector in park_vector_list:
        # print i, len(park_vector_list[i])
        if len(park_vector) == 0:
            similarity_list.extend('0')
        else:
            similarity_list.extend(cal_similarity(np.array(query_vector).reshape(1, -1), np.array(park_vector).reshape(1, -1)))
    park_similarity = pd.DataFrame({
        "Park Name": cleaned_place_name_list,
        "Similarity": similarity_list
    })
    print "These National Parks are recommended to you!"
    sorted_park_similarity = park_similarity.sort_values(by=['Similarity'], ascending=False)
    print sorted_park_similarity.iloc[:10]


if __name__ == '__main__':
    main()
