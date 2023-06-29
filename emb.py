import pandas as pd
import pickle
from openai.embeddings_utils import get_embedding, cosine_similarity
import numpy as np
import openai
import gradio as gr

# Load the entire DataFrame (including embeddings) from a pickle file
with open('df_with_embeddings.pkl', 'rb') as f:
    df = pickle.load(f)

# Set up your OpenAI API key
openai.api_key = "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"

# Initialize the messages list with the system message
messages = [
{
    "role": "system", 
    "content": "you are an exam assistant helping a student, You have access to a large corpus of text data, and your function is to sift through this knowledge to identify the most relevant piece of information to any given query. asnwer with the information in the most similar document from the corpus. your answer should be brief, and short, go straight to the point. "
   # "content": "You are an AI assistant with the task of helping a student understand various subjects. You have access to a large corpus of text data, and your function is to sift through this knowledge to identify the most relevant piece of information to any given query. Your responses should provide clear, detailed explanations based on the information in the most similar document from the corpus. Aim to engage the student in a conversational manner, and promote understanding of underlying concepts rather than simply providing answers."
}
]

def generate_answer(user_query):
    global messages
    
    # Append user message to messages
    messages.append({"role": "user", "content": user_query})

    # Embed the user query
    query_embedding = get_embedding(user_query, engine='text-embedding-ada-002')

    # Compute cosine similarities
    df['Cosine_Similarity'] = df['Full_Text_Embedding'].apply(lambda x: cosine_similarity(np.array(x), query_embedding))

    # Sort by similarity
    df_sorted_by_similarity = df.sort_values('Cosine_Similarity', ascending=False)

    # Get the index of the most similar document in the original dataframe
    most_similar_doc_index = df_sorted_by_similarity.index[0]

    # Get the most similar document
    most_similar_document = df.loc[most_similar_doc_index]

    # Define the context and the question
    context = most_similar_document['Full_Text']
    question = user_query

    # Generate an answer to the question based on the context
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=messages,
        max_tokens=150
    )

    # Extract the AI's message from the response
    ai_message = response['choices'][0]['message']['content']

    # Append AI message to messages
    messages.append({"role": "assistant", "content": ai_message})

    return ai_message

# Define Gradio interface
iface = gr.Interface(fn=generate_answer, inputs="text", outputs="text")

iface.launch(share=True, debug=True)

