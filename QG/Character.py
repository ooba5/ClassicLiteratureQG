from cgi import print_form


class Character:

    def __init__(self, pn):
        self.primary_name = pn
        self.name_frequency = 1
        self.all_names = []
        self.all_names.append(pn)
        self.comp_scores_ot = []
        for n in pn.split(" "):
            self.all_names.append(n)

    def __init__(self, pn, sent_dict):
        self.primary_name = pn
        self.name_frequency = 1
        self.all_names = []
        self.all_names.append(pn)
        for n in pn.split(" "):
            self.all_names.append(n)
        self.neg_score = sent_dict["neg"]
        self.pos_score = sent_dict["pos"]
        self.neut_score = sent_dict["neu"]
        self.comp_score = sent_dict["compound"]
        self.comp_scores_ot = []
        self.relationship_count = {}
        self.relationship_sentiment = {}


    def update_sent_scores(self,sent_dict):
        self.neg_score+=sent_dict["neg"]
        self.pos_score+=sent_dict["pos"]
        self.neut_score += sent_dict["neu"]
        self.comp_score += sent_dict["compound"]
        self.comp_scores_ot.append(sent_dict["compound"])
    def get_sent_scores(self):
        '''Returns normalized positivivy and negativity score, normalized by name count'''
        return {"pos":self.pos_score/self.name_frequency, "neg":self.neg_score/self.name_frequency,
        "neutral":self.neut_score/self.name_frequency, "compound":self.comp_score/self.name_frequency}

    def get_positivity_ratio(self):
        '''Returns pos score / neg score ~ 1 is neural, >1 is positive, and <1 is negative'''
        if self.neg_score > 0:
            return self.pos_score/self.neg_score
        else:
            return self.pos_score
    def get_pos_index(self, tot_pos):
        return self.pos_score/tot_pos
    
    def get_neg_index(self, tot_neg):
        return self.neg_score/tot_neg

    def __str__(self):
        return self.primary_name

    def count_appearance(self, ca = 1):
        self.name_frequency += ca

    def __lt__(self, other_char):
        if self.name_frequency < other_char.name_frequency:
            return True 
        else:
            return False 
    

    def __eq__(self, other_char):
        if self.name_frequency == other_char.name_frequency:
            return True 
        else:
            return False
    
    def __str__(self):
        return self.primary_name
    