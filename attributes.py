# -*- coding: utf-8 -*-
"""
Created on June 3rd, 2017
@author: Mengyin Liu
"""

import pandas as pd
import numpy as np
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import re

output1 = pd.read_csv('/Users/mliu/National_Parks/data/review_output0-10.csv', encoding='utf-8')
output2 = pd.read_csv('/Users/mliu/National_Parks/data/review_output10-20.csv', encoding='utf-8')
output3 = pd.read_csv('/Users/mliu/National_Parks/data/review_output20-30.csv', encoding='utf-8')
output4 = pd.read_csv('/Users/mliu/National_Parks/data/review_output30-40.csv', encoding='utf-8')
output5 = pd.read_csv('/Users/mliu/National_Parks/data/review_output40-50.csv', encoding='utf-8')
output6 = pd.read_csv('/Users/mliu/National_Parks/data/review_output50-60.csv', encoding='utf-8')

review_table = pd.concat([output1,output2, output3,output4, output5, output6])

review_array = review_table[review_table["Park Name"] == 'Yosemite National Park']['Review']
review_array = review_table[review_table["Things To Do"] == 'Bear Lake']['Review']


# get the attribute chunk for each things to do
def attribute_chunk (review_array, key_word):

    lmtzr = WordNetLemmatizer()

    attribute_list = []
    all_words_list = []
    for review in review_array:
        letters_only = re.sub("[^a-zA-Z]", " ", review)
        tokenized_review = word_tokenize(letters_only.strip().lower())
        stop = stopwords.words('english')
        lemmatize_review = np.array([lmtzr.lemmatize(w) for w in tokenized_review if not w in stop])

        if key_word in lemmatize_review:
            key_index = np.where(lemmatize_review == key_word)[0]
            for index in key_index:
                new_index = range(max(index-3,0),min(index+4, len(lemmatize_review)))
                attribute_list.append(lemmatize_review[new_index])
                all_words_list.extend(lemmatize_review[new_index])

    return attribute_list, all_words_list

def lift_score (things_to_do, key_word, aspect_list):
    lmtzr = WordNetLemmatizer()

    review_array = review_table[review_table["Things To Do"] == things_to_do]['Review']

    lift_score_list = []
    word_list = []
    for aspect in aspect_list:
        all_counter = 0
        key_word_counter = 0
        aspect_counter = 0
        both_counter = 0
        for review in review_array:
            letters_only = re.sub("[^a-zA-Z]", " ", review)
            tokenized_review = word_tokenize(letters_only.strip().lower())
            stop = stopwords.words('english')
            lemmatize_review = np.array([lmtzr.lemmatize(w) for w in tokenized_review if not w in stop])
            all_counter += 1
            if key_word in lemmatize_review:
                key_word_counter += 1
            if aspect in lemmatize_review:
                aspect_counter += 1
            if (key_word in lemmatize_review) & (aspect in lemmatize_review):
                both_counter += 1

        all_counter = all_counter * 1.00
        lift_score = (both_counter / all_counter) / ((key_word_counter / all_counter) * (aspect_counter / all_counter))
        lift_score_list.append(lift_score)
        word_list.append(aspect)

    return lift_score_list, word_list

# lift_score('Bear Lake', key_word, aspect_list=hike_table[hike_table['Things To Do'] == 'Bear Lake']['ADJ'])


def key_word_table (key_word):

    park_name_list = []
    things_to_do_list = []
    top_adj_list = []
    top_count_list = []

    for row in review_table[['Park Name', 'Things To Do']].drop_duplicates().itertuples():
        park_name = row._1
        things_to_do = row._2
        review_array = review_table[review_table["Things To Do"] == row._2]['Review']

        attribute_list, all_words_list = attribute_chunk(review_array, key_word)

        part_of_speech = nltk.pos_tag(all_words_list)

        freq_dist = nltk.FreqDist(w for w in part_of_speech)
        most_common = freq_dist.most_common(30)

        adj_list = []
        adj_count = []
        for (pair, count) in most_common:
            if (pair[1] in ['JJ', 'JJS', 'JJR']) & (pair[0] != key_word):
                adj_list.append(pair[0])
                adj_count.append(count)

        num_adj = len(adj_list)
        top_adj_list.extend(adj_list)
        top_count_list.extend(adj_count)
        park_name_list.extend([park_name]*num_adj)
        things_to_do_list.extend([things_to_do]*num_adj)

    attribute_table2 = pd.DataFrame([park_name_list, things_to_do_list, top_adj_list, top_count_list]).transpose()
    attribute_table2.columns = ["Park Name", "Things To Do", 'ADJ', 'Count']

    attribute_table = pd.DataFrame([park_name_list, things_to_do_list, top_adj_list, top_count_list]).transpose()
    attribute_table.columns = ["Park Name", "Things To Do", 'ADJ', 'Count']

    things_to_do_list = []
    lift_score_list = []
    all_word_list = []
    for item in attribute_table2['Things To Do'].drop_duplicates().iteritems():
        print item[1]
        score_list, word_list = lift_score(item[1], key_word, attribute_table2[attribute_table2['Things To Do'] == item[1]]['ADJ'])
        lift_score_list.append(score_list)
        all_word_list.append(word_list)

        num_score = len(score_list)
        things_to_do_list.extend([item[1]] * num_score)
        print num_score
        print lift_score_list
        print word_list
        print things_to_do_list

    list_table2 = pd.DataFrame([things_to_do_list, all_word_list, lift_score_list]).transpose()
    list_table2.columns = ["Things To Do", 'ADJ','Lift Score']


def main():

    key_word = 'hike'
    key_word_table(key_word)

if __name__ == '__main__':

