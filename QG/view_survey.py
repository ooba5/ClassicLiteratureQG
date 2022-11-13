import pandas as pd 
import matplotlib.pyplot as plt 

df = pd.read_csv("response.txt")

each_df = []
for c in df.columns:
 each_df.append(df.groupby(c).size() )

df2 = pd.concat(each_df[1:-1]).reset_index()

df_final = df2.groupby("index").sum().reset_index()
df_final[0] = df_final[0].astype(int) /sum(df_final[0])
print(df_final.head())
df_final["index"] = df_final["index"].apply(lambda x: " ".join([w +"\n" if e % 5 == 0 else w for e,w in enumerate(x.split(" "))]))
plt.bar(df_final["index"], df_final[0])
plt.xticks(rotation = 30)
plt.tight_layout()
plt.title("Survey Results")
plt.ylabel("Percentage of Responses")
plt.xlabel("Response")
plt.show()

# df2.to_csv("df_edited.csv")