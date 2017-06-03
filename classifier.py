# -*- coding: utf-8 -*-

# The purpose of this script is to run Naive Bayes Classifier for each park in interest

import pandas as pd
import numpy as np
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
from collections import Counter
import random
import re
import nltk


output1 = pd.read_csv('/Users/mliu/National_Parks/data/review_output0-10.csv', encoding='utf-8')
output2 = pd.read_csv('/Users/mliu/National_Parks/data/review_output10-20.csv', encoding='utf-8')
output3 = pd.read_csv('/Users/mliu/National_Parks/data/review_output20-30.csv', encoding='utf-8')
output4 = pd.read_csv('/Users/mliu/National_Parks/data/review_output30-40.csv', encoding='utf-8')
output5 = pd.read_csv('/Users/mliu/National_Parks/data/review_output40-50.csv', encoding='utf-8')
output6 = pd.read_csv('/Users/mliu/National_Parks/data/review_output50-60.csv', encoding='utf-8')
wiki_table = pd.read_csv('/Users/mliu/National_Parks/data/wiki_output.csv')

review_table = pd.concat([output1,output2, output3,output4, output5, output6])

review_table.groupby(["Park Name", "Review Rating"]).size()


# tokenize and remove stop words for reviews
def review_tokenizer (park_data):

    park_data['Review Rating'] = np.where(park_data["Review Rating"] >= 4.0, 'pos', 'neg')
    # create tuples for all the reviews and rating
    all_review_pairs = []
    for row in park_data.itertuples():
        all_review_pairs.append((row.Review, row._2))

    lmtzr = WordNetLemmatizer()

    preprocess_review_list = []
    all_words = []
    for (review, rating) in all_review_pairs:
        letters_only = re.sub("[^a-zA-Z]", " ", review)
        tokenized_review = word_tokenize(letters_only.strip().lower())
        stop = stopwords.words('english')
        lemmatize_review = [lmtzr.lemmatize(w) for w in tokenized_review if not w in stop]
        preprocess_review_list.append((lemmatize_review,rating))
        all_words.extend(lemmatize_review)

    freq_dist = nltk.FreqDist(w.lower() for w in all_words)
    all_words = [word for (word,count) in freq_dist.most_common(8000)]

    return preprocess_review_list, all_words


def classifier_dataprep (preprocess_review_list, all_words):

    classifier_data = []
    for (review, rating) in preprocess_review_list:
        word_dict = {}
        for word in all_words:
            word_dict[word] = (word in review)

        classifier_data.append((word_dict,rating))

    return classifier_data


def train_test (data):
    random.seed(10)
    random.shuffle(data)
    train_data = data[:int(len(data)*0.6)]
    test_data = data[int(len(data)*0.6):]

    return train_data, test_data


def main():

    park_name = 'Yellowstone National Park'
    park_data = review_table[review_table["Park Name"] == park_name ][['Review', 'Review Rating']]
    preprocess_review_list, all_words = review_tokenizer(park_data)
    classifier_data = classifier_dataprep(preprocess_review_list, all_words)
    train_data, test_data = train_test(classifier_data)

    classifier = nltk.NaiveBayesClassifier.train(train_data)
    print(nltk.classify.accuracy(classifier, test_data))
    classifier.show_most_informative_features(20)


    # create confusion matrix
    testoutput=[]
    for (review,rating) in test_data:
        a = classifier.classify(review)
        testoutput.append(a)
    actual=[]
    for (review,rating) in test_data:
        actual.append(rating)

    cm = nltk.ConfusionMatrix(actual, testoutput)
    print cm


    # get the reviews with informative key words
    for i in range(len(preprocess_review_list)):
        if 'chinese' in preprocess_review_list[i][0]:
            print park_data.iloc[i]['Review']


if __name__ == "__main__":
    main()



















