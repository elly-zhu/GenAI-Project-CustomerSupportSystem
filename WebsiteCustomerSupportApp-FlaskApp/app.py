from flask import Flask, redirect, render_template, request, url_for
import os
import openai
import numpy as np
import pandas as pd
from ast import literal_eval
from urllib.parse import urlparse
import subprocess
from bs4 import BeautifulSoup
from collections import deque
from html.parser import HTMLParser
from urllib.parse import urlparse
from openai.embeddings_utils import distances_from_embeddings, cosine_similarity
from ast import literal_eval
from datetime import date
import sys
import matplotlib


app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

crawler_output = None
embedding_output = None
answer_output = None


@app.route('/')
def main():
    global crawler_output
    global embedding_output
    global answer_output
    return render_template('index.html', crawler_output=crawler_output, embedding_output=embedding_output, answer_output=answer_output)


@app.route('/step1', methods=("GET", "POST"))
def handle_step1():
    if request.method == "POST":
        try:
            global crawler_output
            domain_name = request.form['domainName']
            full_url = request.form['fullUrl']
            scraped_file_path = request.form['scrapedFilePath']
            limit = request.form['limit']
            result = subprocess.run(["python3", "crawler.py", "setup_crawler", domain_name,
                                    full_url, scraped_file_path, limit], capture_output=True, text=True)
            # Simulate an error for demonstration purposes
            # Uncomment the line below to test error handling
            # raise ValueError("This is a simulated error")
            result = str(result).split('\\n')
            print(result)
            result = [line for line in result if len(line) > 1]
            crawler_output = result
            return render_template('index.html', crawler_output=crawler_output)
        except Exception as e:
            print("An error occurred: " + str(e), "error")
            return redirect(url_for('main'))


@app.route("/step2", methods=("GET", "POST"))
def handle_step2():
    if request.method == "POST":
        try:
            scrapedFilePath = request.form["scrapedFilePath"]
            global embedding_output
            result = subprocess.run(
                ["python3", "embedding.py", scrapedFilePath], capture_output=True, text=True)

            result = str(result).split('\\n')
            result = [line for line in result if len(line) > 1]
            embedding_output = result
            return render_template('index.html', embedding_output=embedding_output)
        except Exception as e:
            print("An error occurred: " + str(e), "error")
            return redirect(url_for('main'))


@app.route("/step3", methods=("GET", "POST"))
def handle_step3():
    if request.method == "POST":
        try:
            global answer_output
            embeddingFile = request.form["embeddingFile"]
            question = request.form["question"]

            result = subprocess.run(
                ["python3", "answer.py", embeddingFile, question], capture_output=True, text=True)
            result = str(result)
            result = result.split('stdout=')[1].replace(
                "'", "").split('\\n')[:-1]
            answer_output = result
            return render_template('index.html/', answer_output=answer_output)
        except Exception as e:
            print("An error occurred: " + str(e), "error")
            return redirect(url_for('main'))

        # response = openai.Completion.create(
        #     model="text-davinci-003",
        #     prompt=generate_prompt(question),
        #     temperature=0.6,
        # )
        # return redirect(url_for("index", result=response.choices[0].text))


# def generate_prompt(question):
#     return """Suggest three names for an animal that is a superhero.

# Animal: Cat
# Names: Captain Sharpclaw, Agent Fluffball, The Incredible Feline
# Animal: Dog
# Names: Ruff the Protector, Wonder Canine, Sir Barks-a-Lot
# Animal: {}
# Names:""".format(
#         animal.capitalize()
#     )
