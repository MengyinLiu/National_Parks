# -*- coding: utf-8 -*-
"""
@author: Mengyin Liu
"""

import pandas as pd
from gensim import corpora
import gensim
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk
import re
import random


output1 = pd.read_csv('/Users/mliu/National_Parks/data/review_output0-10.csv', encoding='utf-8')
output2 = pd.read_csv('/Users/mliu/National_Parks/data/review_output10-20.csv', encoding='utf-8')
output3 = pd.read_csv('/Users/mliu/National_Parks/data/review_output20-30.csv', encoding='utf-8')
output4 = pd.read_csv('/Users/mliu/National_Parks/data/review_output30-40.csv', encoding='utf-8')
output5 = pd.read_csv('/Users/mliu/National_Parks/data/review_output40-50.csv', encoding='utf-8')
output6 = pd.read_csv('/Users/mliu/National_Parks/data/review_output50-60.csv', encoding='utf-8')
yellowstone = pd.read_csv('/Users/mliu/National_Parks/data/review_output_yellowstone.csv', encoding='utf-8')

review_table = pd.concat([output1,output2, output3,output4, output5, output6])


review_sample = yellowstone['Review'] #random.sample(yellowstone['Review'],1000)
# review_sample = yellowstone['Review'][500:1000]
review_sample = review_table['Review']
# review_sample = random.sample(review_sample,20000)
review_sample_train = review_table[review_table["Things To Do"] == 'Bear Lake']['Review'][:500]
review_sample_test = review_table[review_table["Things To Do"] == 'Bear Lake']['Review'][500:1000]


def tokenizer (review_array):

    lmtzr = WordNetLemmatizer()

    all_reviews = []
    for review in review_array:
        letters_only = re.sub("[^a-zA-Z]", " ", review)
        tokenized_review = word_tokenize(letters_only.strip().lower())
        tag_review = nltk.pos_tag(tokenized_review)
        stop = stopwords.words('english')
        # keep only noun and only non-stop words
        lemmatize_review = [lmtzr.lemmatize(w) for (w,tag) in tag_review if (w not in stop) & (tag in ['NN', 'NNS'])]
        all_reviews.append(lemmatize_review)

    return all_reviews

all_reviews = tokenizer(review_sample)

dictionary = corpora.Dictionary(all_reviews)

# dictionary.filter_extremes(no_below=40, no_above=0.2)

corpus = [dictionary.doc2bow(text) for text in all_reviews]

tfidf = gensim.models.TfidfModel(corpus)
corpus_tfidf = tfidf[corpus]

ldamodel = gensim.models.ldamodel.LdaModel(corpus, num_topics=20, id2word = dictionary, alpha='auto', )

for index, score in sorted(ldamodel[corpus[0]], key=lambda tup: -1*tup[1]):
    print "Score: {}\t Index:{}\t Topic: {}".format(score, index, ldamodel.print_topic(index, 10))

for topic in ldamodel.print_topics(num_topics=20, num_words=5):
    print topic


# for topic in ldamodel.show_topics():
#     print topic

# ldamodel.get_term_topics('water')
# ldamodel.get_document_topics(corpus)