import pandas as pd

print("Reading XLS...")

df = pd.read_excel("data/data_players.xls")

print("Saving CSV...")

df.to_csv("data/players_clean.csv", index=False)

print("Converted to CSV successfully")