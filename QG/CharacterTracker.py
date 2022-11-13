from Character import Character
class CharacterTracker:

    def __init__(self):
        
        self.all_chars = []
        self.pos_score = 0
        self.neg_score = 0
        self.total_name_freq = 0
    def new_char(self, new_name, sent_scores):
        '''Adds new character, checks for existing character, if first name of the new
        charracters name is part of an existing character, then that character is added to that character,
        otherwise creates a new character'''
        found_char = 0
        for each_c in self.all_chars:
            for each_n in new_name.split(" "):
                if each_n in each_c.all_names:
                    found_char = 1
                    if new_name not in each_c.all_names:
                        each_c.all_names.append(new_name)
                    # if len(new_name) > len(each_c.primary_name):
                    #     each_c.primary_name = new_name
                    each_c.count_appearance()
                    self.total_name_freq += 1
                    each_c.update_sent_scores(sent_scores)
        if found_char == 0:
            self.all_chars.append(Character(new_name,sent_scores))
            self.total_name_freq += 1

    def new_char_from_network(self, new_name, sent_scores, prev_appearance):
        found_char = 0
        for each_c in self.all_chars:
            for each_n in new_name.split(" "):
                if each_n in each_c.all_names:
                    found_char = 1
                    if new_name not in each_c.all_names:
                        each_c.all_names.append(new_name)

                    each_c.count_appearance(ca=prev_appearance)
                    self.total_name_freq += 1
                    each_c.update_sent_scores(sent_scores)
            if found_char == 0:
                self.all_chars.append(Character(new_name,sent_scores))
                self.total_name_freq += 1
    def add_char_relation(self, name, other_name, sent_scores={}):
        c1 = self.get_char_by_name(name)
        c2 = self.get_char_by_name(other_name)
        if c1.primary_name in c2.relationship_count.keys():
            c1.relationship_count[c2.primary_name] += 1
            c2.relationship_count[c1.primary_name] += 1
            c1.relationship_sentiment[c2.primary_name] += sent_scores["compound"]
            c2.relationship_sentiment[c1.primary_name] += sent_scores["compound"]
        else:
            c2.relationship_sentiment[c1.primary_name] = sent_scores["compound"]
            c1.relationship_sentiment[c2.primary_name] = sent_scores["compound"]
            c1.relationship_count[c2.primary_name] = 1
            c2.relationship_count[c1.primary_name] = 1
    def __iter__(self):
        '''Returns iterated of sorted all chars by name mentions, from high to low'''
        return iter(sorted(self.all_chars, reverse = True))

    def get_top_characters(self, percent=50):
        '''Returns top percent (int to be divided by 100) mentioned characters in list'''
        return sorted(self.all_chars, reverse=True)[0:int(len(self.all_chars) * percent // 100)]
    
    def get_top_characters_by_count(self, num):
        return sorted(self.all_chars, reverse=True)[0:num]

    def get_top_characters_by_min_mention(self, num):
        chars = self.get_top_characters()
        select_chars = []
        for c in chars:
            if c.name_frequency > num: select_chars.append(c)
        return select_chars
    def set_total_scores(self):
        #TODO: Is NOrmalized?
        for c in self.all_chars:
            s = c.get_sent_scores()
            self.pos_score += s["pos"]
            self.neg_score += s["neg"]
            self.total_name_freq += c.name_frequency
        # self.pos_score/=self.total_name_freq
        # self.neg_score/=self.total_name_freq

    def get_char_by_name(self, name):
        '''Retrieve character by name'''
        for i in self.get_top_characters(percent=100):
            if (name in i.all_names):
                return i
    
    def avg_name_freq(self, ment):
        l_of_c = []
        for c in self.get_top_characters_by_min_mention(ment):
            l_of_c.append(c.name_frequency)
        return sum(l_of_c)/len(l_of_c)
