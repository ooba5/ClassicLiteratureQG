
import enum
import spacy 
import sys
from Character import Character
from CharacterTracker import CharacterTracker

import networkx as nx 
import matplotlib.pyplot as plt 
import numpy as np

import logging 
logging.basicConfig(filename="qgLog.log",filemode="w",level=logging.INFO)
logging.info("Beginning QG Log For new Book")
logging.basicConfig(filemode="a")
#help from spacy documentation https://spacy.io/usage/processing-pipelines
#spacy models availble: https://spacy.io/models/en


if len(sys.argv) != 2:
    print("Please enter Desired input: python characterNER.py PATH_TO_FILE")
    exit()
INPUT_TEXT = sys.argv[1]


#nltk portion 
nlp = spacy.load("en_core_web_lg")

from nltk.sentiment.vader import SentimentIntensityAnalyzer

sia = SentimentIntensityAnalyzer()
all_chars = CharacterTracker()
count = 0
count_char_between = 0
prev_line = ""
chars_in_range = []
max_line_distance = 75
count_avg_line_len = []
words_between = ""
try: 
    open(INPUT_TEXT)
except FileNotFoundError:
    print("File: " + INPUT_TEXT + " Was not found")
    exit()

with open(INPUT_TEXT) as book:
    entire_book = [*book]
logging.info(f'Number of Lines Total {len(entire_book)}')
entire_book = [e for e in entire_book if e != "\n"]
entire_book_simplified = [entire_book[e1] + entire_book[e1 +1] + entire_book[e1 +2] for e1 in range(0,len(entire_book)-3, 3)]

logging.info(f'Number of Lines Simplified {len(entire_book_simplified)}')
for each_l in entire_book:

    count_char_between += 3
    words_between += each_l
    if count_char_between > max_line_distance:
        chars_in_range = []
        count_char_between = 0
        words_between = ""

    each_l_classified = nlp(each_l)
    if(len(each_l_classified) > 0):
        for each_ent in each_l_classified.ents:
            
            if(each_ent.label_ == "PERSON"):
                c_name = each_ent.text.lower().replace("’s", '').replace("'s", "").replace("\n", "").replace ("chapter", "").replace("gutenberg", "").replace(":","").replace("-","").replace("/","").replace("\\","").replace("_","").replace("i. ", "")
                all_chars.new_char(c_name, sia.polarity_scores(prev_line + each_l))
                if c_name not in chars_in_range:
                    chars_in_range.append(c_name)
                if(len(chars_in_range)>=2):
                    for char_a in chars_in_range:
                        for char_b in chars_in_range:
                            if all_chars.get_char_by_name(char_a).primary_name != all_chars.get_char_by_name(char_b).primary_name:
                                all_chars.add_char_relation(char_a,char_b, sia.polarity_scores(words_between))
                
                if len(chars_in_range) >=5:
                    
                    words_between = ""
                    count_char_between = 0
                    chars_in_range = []
                
                    
    prev_line = each_l  
  
     

MIN_MENTION = 15
count_G = nx.Graph()
all_chars.set_total_scores()
#Rank the Characters by sentiment 
char_sentiment_norm = {}
max_weight = 0
for char_node in all_chars.get_top_characters_by_min_mention(MIN_MENTION):
    char_sentiment_norm[char_node.primary_name] = char_node.comp_score
    if(char_node.name_frequency > max_weight):
        max_weight = char_node.name_frequency
for i,each_c in enumerate(sorted(char_sentiment_norm.items(), key = lambda kv: kv[1], reverse=False)):
    char_sentiment_norm[each_c[0]] = i 

logging.info(f'MAX WEIGHT IS {max_weight}')

max_sentiment = abs(np.mean([np.mean([*c.relationship_sentiment.values()]) for c in all_chars.get_top_characters_by_min_mention(MIN_MENTION)]))
logging.info(f'MAX SENT IS {max_sentiment}')
for char_node in all_chars.get_top_characters_by_min_mention(MIN_MENTION):
    #Their Sentiment is Just a Ranked Version
    sentiment = char_sentiment_norm[char_node.primary_name]
    
    count_G.add_node(char_node.primary_name, weight = char_node.name_frequency, sentiment = sentiment)
    for other_node,weight in char_node.relationship_count.items():
        if other_node in [c.primary_name for c in all_chars.get_top_characters_by_min_mention(MIN_MENTION)] and weight >= 10:
            
            if ~count_G.has_edge(char_node.primary_name, other_node):
                count_G.add_edge(char_node.primary_name, other_node, weight=weight/max_weight, sentiment = char_node.relationship_sentiment[other_node]/max_sentiment)


fig, ax = plt.subplots(1,1, figsize = (int(len(count_G.nodes)* 1.5), int(len(count_G.nodes)* 2)))
ax.set_facecolor("grey")
#Remove Isolated nodes
bad_nodes = []
for each_n in count_G.nodes:
    if(nx.degree(count_G, each_n) < 1):
        bad_nodes.append(each_n)
count_G.remove_nodes_from(bad_nodes)


#Draw Graph 
nx.draw(count_G, node_size = [c[1]["weight"] for c in count_G.nodes(data=True)],
with_labels = True,  node_color = [c[1]["sentiment"] for c in count_G.nodes(data = True)],
cmap =plt.cm.bwr.reversed(), width=[e[2]["weight"] for e in count_G.edges(data=True)]/np.mean([e[2]["weight"] for e in count_G.edges(data=True)]),edge_color=[e[2]["sentiment"] for e in count_G.edges(data=True)],
edge_cmap =plt.cm.bwr.reversed(), font_color = "cyan", ax = ax)

fig.savefig("count_and_sentiment_G.png", facecolor=ax.get_facecolor())
nx.write_gml(count_G, "count_and_sentiment_G.gml")

#All Characters and their overtime sentiment score for tracking over course of book 
ot_chars = {}
for c in all_chars.get_top_characters_by_min_mention(MIN_MENTION):
    ot_chars[c.primary_name] = c.comp_scores_ot 

import json
with open("char_sent_ot.json", "w") as ot_write:
    json.dump(ot_chars, ot_write, indent=2)

logging.shutdown()

import QuestionTemplates
                    