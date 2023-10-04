
from urllib.parse import urlparse
import os
import pandas as pd
from openai.embeddings_utils import distances_from_embeddings, cosine_similarity
from ast import literal_eval
import openai
import tiktoken
import time
import sys


def split_into_many(text, max_tokens=500):

    tokenizer = tiktoken.get_encoding("cl100k_base")

    # Split the text into sentences
    sentences = text.split('. ')
    # Get the number of tokens for each sentence
    n_tokens = [len(tokenizer.encode(" " + sentence))
                for sentence in sentences]
    chunks = []
    tokens_so_far = 0
    chunk = []

    # Loop through the sentences and tokens joined together in a tuple
    for sentence, token in zip(sentences, n_tokens):

        # If the number of tokens so far plus the number of tokens in the current sentence is greater
        # than the max number of tokens, then add the chunk to the list of chunks and reset
        # the chunk and tokens so far
        if tokens_so_far + token > max_tokens:
            chunks.append(". ".join(chunk) + ".")
            chunk = []
            tokens_so_far = 0

        # If the number of tokens in the current sentence is greater than the max number of
        # tokens, go to the next sentence
        if token > max_tokens:
            continue

        # Otherwise, add the sentence to the chunk and add the number of tokens to the total
        chunk.append(sentence)
        tokens_so_far += token + 1

    # Add the last chunk to the list of chunks
    if chunk:
        chunks.append(". ".join(chunk) + ".")

    return chunks


################################################################################
# Step 10
################################################################################

# Note that you may run into rate limit issues depending on how many files you try to embed
# Please check out our rate limit guide to learn more on how to handle this: https://platform.openai.com/docs/guides/rate-limits


def generate_embeddings(text):
    print("generate_embeddings running..")
    while True:
        try:
            response = openai.Embedding.create(
                input=text, engine='text-embedding-ada-002')
            if 'data' in response and response['data']:
                return response['data'][0]['embedding']
            else:
                return None
        except openai.error.RateLimitError as e:
            wait_time = 20  # Default wait time in seconds
            if 'Retry-After' in e.headers:
                wait_time = int(e.headers['Retry-After'])
            print(f"Rate limit reached. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)


def process_and_save_embeddings(df, embedded_csv_filepath="processed/embeddings.csv"):
    print("process_and_save_embeddings running..")
    embeddings = []

    for text in df['text']:
        embedding = generate_embeddings(text)
        if embedding:
            embeddings.append(embedding)
        else:
            embeddings.append(None)

    df['embeddings'] = embeddings
    df.to_csv(embedded_csv_filepath)
    print(f"=> {embedded_csv_filepath} created.")
    print("First 5 rows")
    print(df.head())


def init_api():
    with open(".env") as env:
        for line in env:
            key, value = line.strip().split("=")
            os.environ[key] = value

    openai.api_key = os.environ.get("OPENAI_API_KEY")
    openai.organization = os.environ.get("ORG_ID")


# Assuming you have a DataFrame called 'df' with a 'text' column
# and you want to generate embeddings for each text and save them
# to a CSV file


def main():
    scraped_csv_filepath, scraped_csv_filename = os.path.split(
        scraped_csv_fullpath)
    embedded_csv_filepath = os.path.join(scraped_csv_filepath, "embedding.csv")

    ################################################################################
    # Step 7
    ################################################################################

    # Load the cl100k_base tokenizer which is designed to work with the ada-002 model
    tokenizer = tiktoken.get_encoding("cl100k_base")

    df = pd.read_csv(scraped_csv_fullpath, index_col=0)
    df.columns = ['title', 'text']

    # Tokenize the text and save the number of tokens to a new column
    df['n_tokens'] = df.text.apply(lambda x: len(tokenizer.encode(x)))

    # Visualize the distribution of the number of tokens per row using a histogram
    df.n_tokens.hist()

    ################################################################################
    # Step 8
    ################################################################################

    # Function to split the text into chunks of a maximum number of tokens
    max_tokens = 500

    shortened = []

    # Loop through the dataframe
    for row in df.iterrows():

        # If the text is None, go to the next row
        if row[1]['text'] is None:
            continue

        # If the number of tokens is greater than the max number of tokens, split the text into chunks
        if row[1]['n_tokens'] > max_tokens:
            shortened += split_into_many(row[1]['text'])

        # Otherwise, add the text to the list of shortened texts
        else:
            shortened.append(row[1]['text'])

    ################################################################################
    # Step 9
    ################################################################################

    df = pd.DataFrame(shortened, columns=['text'])
    df['n_tokens'] = df.text.apply(lambda x: len(tokenizer.encode(x)))
    df.n_tokens.hist()

    init_api()

    process_and_save_embeddings(df, embedded_csv_filepath)


if __name__ == "__main__":
    # Check for the function name argument
    if len(sys.argv) != 2:
        print("Usage: python3 embedding.py <scraped_csv_file_path>")
        sys.exit(1)
    scraped_csv_fullpath = sys.argv[1]
    if os.path.exists(scraped_csv_fullpath):
        print(f'The file "{scraped_csv_fullpath}" exists.')
        main()
    else:
        print(f'The file "{scraped_csv_fullpath}" does not exist.')
        exit()
