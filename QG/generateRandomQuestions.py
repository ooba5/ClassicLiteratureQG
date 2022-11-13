import numpy as np 
selected = np.random.randint(0, 192, 30)
print(selected)
with open("questions_and_answers.txt") as all_questions:
    for c, each_q  in enumerate(all_questions):
        if c in selected:
            print(each_q)