# -*- coding: utf-8 -*-
"""
Create on June, 4th, 2017
@author: Mengyin Liu
"""

import pandas as pd
import wordcloud
import matplotlib.pyplot as plt
import random

output1 = pd.read_csv('/Users/mliu/National_Parks/data/review_output0-10.csv')
output2 = pd.read_csv('/Users/mliu/National_Parks/data/review_output10-20.csv')
output3 = pd.read_csv('/Users/mliu/National_Parks/data/review_output20-30.csv')
output4 = pd.read_csv('/Users/mliu/National_Parks/data/review_output30-40.csv')
output5 = pd.read_csv('/Users/mliu/National_Parks/data/review_output40-50.csv')
output6 = pd.read_csv('/Users/mliu/National_Parks/data/review_output50-60.csv')

review_table = pd.concat([output1,output2, output3,output4, output5, output6])
review_table.to_csv('/Users/mliu/National_Parks/review_table.csv')
hike_table = pd.read_csv('/Users/mliu/National_Parks/data/hike_table.csv', encoding='utf-8')
lake_table = pd.read_csv('/Users/mliu/National_Parks/data/lake_table.csv', encoding='utf-8')
mountain_table = pd.read_csv('/Users/mliu/National_Parks/data/mountain_table.csv', encoding='utf-8')

hike_table.groupby(["ADJ"]).size()

hike_table = hike_table [hike_table['Lift Score'] >= 1.00]
lake_table = lake_table [lake_table['Lift Score'] >= 1.00]
mountain_table = mountain_table [mountain_table['Lift Score'] >= 1.00]


text_list = []
for i in range(len(mountain_table['ADJ'])):
    # text += (lake_table['ADJ'][i] + ' ')*lake_table['Count'][i]
    text_list.extend([mountain_table['ADJ'][i]] * mountain_table['Count'][i])

random.shuffle(text_list)

text = ''
for word in text_list:
    text += ' ' + word



word_cloud = wordcloud.WordCloud(

                      background_color='white',
                      width=1800,
                      height=1400
                     ).generate(text)

plt.imshow(word_cloud)
plt.axis('off')
# plt.savefig('./my_twitter_wordcloud_1.png', dpi=300)
plt.show()

