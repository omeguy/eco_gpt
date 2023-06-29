import pandas as pd
import pickle
import numpy as np
from openai.embeddings_utils import get_embedding
import openai

openai.api_key = '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'

# Load the DataFrame
df = pd.read_csv('sessions.csv')

def embed_text(texts):
    # Compute the embedding for each text in the batch
    embeddings = [get_embedding(text, engine='text-embedding-ada-002') for text in texts]
    return embeddings

# Concatenate all the relevant text columns
df['Full_Text'] = df['Introduction'].fillna('') + " " + df['Learning Outcomes'].fillna('') + " " + df['Content'].fillna('') + " " + df['Summary'].fillna('') + " " + df['Self-Assessment Questions'].fillna('')

# Batch size for API calls
batch_size = 100

# Generate embeddings for the full text in batches
embeddings = []
for i in range(0, len(df), batch_size):
    print(f'Processing batch {i//batch_size+1}...')
    batch_texts = df['Full_Text'].iloc[i:i+batch_size].tolist()
    batch_embeddings = embed_text(batch_texts)
    embeddings.extend(batch_embeddings)

df['Full_Text_Embedding'] = embeddings

# Save the entire DataFrame (including embeddings) to a pickle file
with open('df_with_embeddings.pkl', 'wb') as f:
    pickle.dump(df, f)
