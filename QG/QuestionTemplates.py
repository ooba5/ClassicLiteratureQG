#Question Templates 
import networkx as nx
import numpy as np
import json 
import logging 
from scipy import stats


read_char_net = nx.read_gml("count_and_sentiment_G.gml")


logging.basicConfig(filename="qgLog.log",filemode="a",level=logging.INFO)
logging.info("Starting Question Templates")
logging.info("Reading Character Sentiment over time JSON")


char_sent_ot_file = open("char_sent_ot.json")
char_sent_ot = json.load(char_sent_ot_file)
char_sent_ot_file.close()
logging.info("Done Reading Character Sentiment over time JSON")


class QuestionGenerator:

    def __init__(self, char_net, char_arc):
        self.char_net = char_net
        self.char_arc = char_arc
        self.first_char = ""
        self.second_char = ""
        self.capt = lambda n:" ".join(l.capitalize() for l in n.split(" "))
        #Templates:
        #Centrality Metrics
        self.q_importance = lambda f,s: f"Would you consider {self.capt(f)} or {self.capt(s)} a more frequently occurring character in the story's plot?"
        self.q_importance_TF = lambda c: f"Is {c} a central character?"

        #Edge Data
        self.q_interaction_sentiment = lambda f,s: f"Would you consider {self.capt(f)} and {self.capt(s)} to have a positive relationship?"
        self.q_interaction_signficance = lambda f,s: f"Do {self.capt(f)} and {self.capt(s)} have a significant relationship?"

        # #Node Data
        self.q_protagonist = lambda c: f"Is {self.capt(c)} closer to a protagonist or antagonist?"

        # #TODO: community structure 
        self.q_community = lambda f,s,ans: f"Does {', '.join(self.capt(a) for a in ans)} belong to a group of aquaintances with both {self.capt(f)} and {self.capt(s)}?"
        self.q_community_enemiesT = lambda f,s,e :f"Is {self.capt(e)} an enemy of both {self.capt(f)} and {self.capt(s)} where the three are all grouped often?"
        self.q_community_enemiesF = lambda f,s,e :f"Is {self.capt(e)} an enemy of both {self.capt(f)} and {self.capt(s)} where the three are all grouped often?"
        #Dynamic Network 
        self.q_story_arc = lambda c: f"Does {self.capt(c)}'s story arc trend more positive as time goes on or more negative?"


    def ask_and_answer_q_importance(self, first_char_rank=None, second_char_rank=None):
        if first_char_rank is None:
            first_char_rank = np.random.randint(0, len(self.char_net.nodes))
        if second_char_rank is None:
            second_char_rank = np.random.randint(0, len(self.char_net.nodes))
            while second_char_rank == first_char_rank:
                
                second_char_rank = np.random.randint(0, len(self.char_net.nodes))
        importance = dict(self.char_net.nodes.data("weight"))
        
        importance = dict(sorted(importance.items(), key = lambda kv: kv[1], reverse=True))
        
        name1,name2 = [*importance.items()][first_char_rank],[*importance.items()][second_char_rank]
        question = self.q_importance(name1[0],name2[0])
        answer = name1[0] + " (First Char)" if name1[1] > name2[1] else name2[0] + " (Second Char)"
        
        return question,answer

    def ask_and_answer_q_relationship_significance(self):
        importance = self.char_net.edges.data()
        edge = [*importance][np.random.randint(len(importance))]

        question = self.q_interaction_signficance(edge[0],edge[1])
        answer = "Yes" if edge[2]["weight"] > 0.5 else "No"
        return question, answer

    def ask_and_answer_q_relationship_sentiment(self):
        importance = self.char_net.edges.data()
        count = 0
        w=0
        while count < 10 and w < 0.5:
            count += 1
            edge = [*importance][np.random.randint(len(importance))]
            w = edge[2]["weight"]
        question = self.q_interaction_sentiment(edge[0],edge[1])
        answer = "Yes" if edge[2]["sentiment"] > 0 else "No"
        return question, answer
    
    def ask_and_answer_q_is_importantTF(self):
        cents = nx.degree_centrality(self.char_net)
        rand_char = np.random.randint(0, len(self.char_net.nodes))
        char_name,char_importance = [*cents.items()][rand_char]
        return self.q_importance_TF(char_name), "Yes" if char_importance > 0.5 else "No"

    def ask_and_answer_q_is_protagonist(self):
        rand_char = np.random.randint(0, len(self.char_net.nodes))
        sent = dict(self.char_net.nodes.data("sentiment"))
        char_name,char_rank = [*sent.items()][rand_char]
        answer = "Protagonist" if char_rank >= len(self.char_net.nodes) / 2 else "Antagonist"
        question = self.q_protagonist(char_name)
        return question, answer 

    def get_char_story_arc(self, in_int):
        char_name, arc = [*self.char_arc.items()][in_int]
        arc = [a for a in arc if a != 0]
        arc_smooth = []
        for e, b in enumerate(range(0, len(arc), len(arc)//3)):
            
            if(e < 2):
                arc_smooth.append(np.mean(arc[0+b: len(arc)//3+b]))
            elif(e == 2):
                arc_smooth.append(np.mean(arc[0+b:]))

        return char_name, arc_smooth


    def ask_and_answer_story_arc(self):
        name, arc = self.get_char_story_arc(np.random.randint(len(self.char_arc)))
        story_progress = stats.pearsonr(range(0, len(arc)), arc)
        tries = 0 
        question = "Story Arc Question Not Found"
        answer = "NA"
        while tries < 30 and story_progress[1] > 0.15:
            tries += 1
            name, arc = self.get_char_story_arc(np.random.randint(len(self.char_arc)))
            story_progress = stats.pearsonr(range(0, len(arc)), arc)
            
        if story_progress[1] < 0.15:
            
            question = self.q_story_arc(name)
            answer = "positive" if story_progress[0] > 0 else "negative" 
        return question,answer


    def ask_and_answer_community_friends(self):
        '''Group into Communties, then randomly pick two characters and ask for a third that belongs to the community'''
        try: #The try catch is because I don't think the community algorithm will always converge
            communities = nx.algorithms.community.greedy_modularity_communities(self.char_net, weight = "sentiment")
            coi = list(communities[np.random.randint(0, len(communities))])
            
            first_char_rank = np.random.randint(0, len(coi))
            second_char_rank = np.random.randint(0, len(coi))

            while second_char_rank == first_char_rank: 
                second_char_rank = np.random.randint(0, len(coi))
            name1 = coi[first_char_rank]
            name2 = coi[second_char_rank]
            coi.remove(name1)
            coi.remove(name2)
            answer = []
            for others in coi:
                if self.char_net.has_edge(name1, others) and self.char_net.has_edge(name2, others):
                    if self.char_net.get_edge_data(name1, others)["sentiment"] > 0.5 and self.char_net.get_edge_data(name2, others)["sentiment"] > 0.5:
                        answer.append(others)
            question = self.q_community(name1, name2, answer)
            if len(answer) >= 1:
                return question, "Yes"
            else:
                return "friendly community not found", "NA"
        except:
            return "friendly community not found", "NA"

    def ask_and_answer_community_enemies(self):
        '''Group into Communties, then randomly pick two characters and ask for a third that belongs to the community'''
        try: #The try catch is because I don't think the community algorithm will always converge
            communities = nx.algorithms.community.greedy_modularity_communities(self.char_net)
            coi = list(communities[np.random.randint(0, len(communities))])
            
            first_char_rank = np.random.randint(0, len(coi))
            second_char_rank = np.random.randint(0, len(coi))

            while second_char_rank == first_char_rank: 
                second_char_rank = np.random.randint(0, len(coi))

            name1 = coi[first_char_rank]
            name2 = coi[second_char_rank]

            coi.remove(name1)
            coi.remove(name2)

            enemy_answer = []
            non_enemy_answer = []
            for others in coi:
                if self.char_net.has_edge(name1, others) and self.char_net.has_edge(name2, others):
                    if self.char_net.get_edge_data(name1, others)["sentiment"] < 0 and self.char_net.get_edge_data(name2, others)["sentiment"] < 0:
                        enemy_answer.append(others)
                    else:
                        non_enemy_answer.append(others)
            

            if len(enemy_answer) >= 1:
                question = self.q_community_enemiesT(name1, name2, enemy_answer[0])
                return question, "Yes"
            else:
                question = self.q_community_enemiesT(name1, name2, non_enemy_answer[0])
                return question, "No"
        
        except:

            return "enemy community not found", "NA"

        

qgSystem = QuestionGenerator(read_char_net, char_sent_ot)

logging.info("Created qgSystem Object")
qa_easy = qgSystem.ask_and_answer_q_importance(first_char_rank=0, second_char_rank = np.random.randint(len(qgSystem.char_net.nodes)//3, len(qgSystem.char_net.nodes)))
logging.info("Created Easy important question")

qa_random = qgSystem.ask_and_answer_q_importance()

qa_relationship_sentiment = qgSystem.ask_and_answer_q_relationship_sentiment()
qa_relationship_significance = qgSystem.ask_and_answer_q_relationship_significance()
qa_random_char_important = qgSystem.ask_and_answer_q_is_importantTF()
qa_protagonist = qgSystem.ask_and_answer_q_is_protagonist()

qa_relationship_sentiment2 = qgSystem.ask_and_answer_q_relationship_sentiment()
qa_relationship_significance2 = qgSystem.ask_and_answer_q_relationship_significance()
qa_random_char_important2 = qgSystem.ask_and_answer_q_is_importantTF()
qa_protagonist2 = qgSystem.ask_and_answer_q_is_protagonist()
logging.info("Simple Questions Done")

qa_story_arc = qgSystem.ask_and_answer_story_arc()
qa_community = qgSystem.ask_and_answer_community_friends()
qa_community_enemy = qgSystem.ask_and_answer_community_enemies()

qa_story_arc2 = qgSystem.ask_and_answer_story_arc()
qa_community2 = qgSystem.ask_and_answer_community_friends()
qa_community_enemy2 = qgSystem.ask_and_answer_community_enemies()

logging.info("Community and Story arc questions done \n Writing Questions and answers to file")

each_question = []

if(qa_community[1] != "NA" and qa_community[0] + "|" + str(qa_community[1]) not in each_question):
    each_question.append(qa_community[0] + "|" + str(qa_community[1]))

if(qa_community_enemy[1] != "NA" and qa_community_enemy[0] + "|" + str(qa_community_enemy[1]) not in each_question):
    each_question.append(qa_community_enemy[0] + "|" + str(qa_community_enemy[1]))

if(qa_story_arc[1] != "NA" and qa_story_arc[0] + "|" + str(qa_story_arc[1]) not in each_question):
    each_question.append(qa_story_arc[0] + "|" + str(qa_story_arc[1]))

if(qa_community2[1] != "NA" and qa_community2[0] + "|" + str(qa_community2[1]) not in each_question):
    each_question.append(qa_community2[0] + "|" + str(qa_community2[1]))

if(qa_story_arc2[1] != "NA" and qa_story_arc2[0] + "|" + str(qa_story_arc2[1]) not in each_question):
    each_question.append(qa_story_arc2[0] + "|" + str(qa_story_arc2[1]))

if(qa_community_enemy2[1] != "NA" and qa_community_enemy2[0] + "|" + str(qa_community_enemy2[1]) not in each_question):
    each_question.append(qa_community_enemy2[0] + "|" + str(qa_community_enemy2[1]))

if(qa_random[0] + "|" + str(qa_random[1]) not in each_question):
    each_question.append(qa_random[0] + "|" + str(qa_random[1]))

if(qa_easy[0] + "|" + str(qa_easy[1]) not in each_question):
    each_question.append(qa_easy[0] + "|" + str(qa_easy[1]))

if(qa_relationship_sentiment[0] + "|" + str(qa_relationship_sentiment[1]) not in each_question):
    each_question.append(qa_relationship_sentiment[0] + "|" + str(qa_relationship_sentiment[1]))

if(qa_relationship_significance[0] + "|" + str(qa_relationship_significance[1]) not in each_question):
    each_question.append(qa_relationship_significance[0] + "|" + str(qa_relationship_significance[1]))

if(qa_random_char_important[0] + "|" + str(qa_random_char_important[1]) not in each_question):
    each_question.append(qa_random_char_important[0] + "|" + str(qa_random_char_important[1]))

if(qa_protagonist[0] + "|" + str(qa_protagonist[1]) not in each_question):
    each_question.append(qa_protagonist[0] + "|" + str(qa_protagonist[1]))    

if(qa_relationship_sentiment2[0] + "|" + str(qa_relationship_sentiment2[1]) not in each_question):
    each_question.append(qa_relationship_sentiment2[0] + "|" + str(qa_relationship_sentiment2[1]))    

if(qa_relationship_significance2[0] + "|" + str(qa_relationship_significance2[1]) not in each_question):
    each_question.append(qa_relationship_significance2[0] + "|" + str(qa_relationship_significance2[1]))    

if(qa_random_char_important2[0] + "|" + str(qa_random_char_important2[1]) not in each_question):
    each_question.append(qa_random_char_important2[0] + "|" + str(qa_random_char_important2[1]))    

if(qa_protagonist2[0] + "|" + str(qa_protagonist2[1]) not in each_question):
    each_question.append(qa_protagonist2[0] + "|" + str(qa_protagonist2[1]))    


with open("questions_and_answers.txt", "w") as q_and_a:
    for eq in each_question:
        q_and_a.write(str(eq) + "\n")
    
logging.shutdown()