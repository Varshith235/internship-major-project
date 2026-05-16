import database
import pandas as pd

df = database.get_resolved_tickets()
for index, row in df.iterrows():
    print(f"ID: {row['id']} | Query: '{row['user_query']}' | Ans: '{row['admin_response']}'")
