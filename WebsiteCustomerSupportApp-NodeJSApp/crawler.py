################################################################################
# Step 1
################################################################################

import requests
import re
import urllib.request
from bs4 import BeautifulSoup
from collections import deque
from html.parser import HTMLParser
from urllib.parse import urlparse
import os
import pandas as pd
import numpy as np
from openai.embeddings_utils import distances_from_embeddings, cosine_similarity
from ast import literal_eval
from datetime import date
import sys
import matplotlib

# Regex pattern to match a URL
HTTP_URL_PATTERN = r'^http[s]{0,1}://.+$'

# Create a class to parse the HTML and get the hyperlinks


class HyperlinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        # Create a list to store the hyperlinks
        self.hyperlinks = []

    # Override the HTMLParser's handle_starttag method to get the hyperlinks
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        # If the tag is an anchor tag and it has an href attribute, add the href attribute to the list of hyperlinks
        if tag == "a" and "href" in attrs:
            self.hyperlinks.append(attrs["href"])

################################################################################
# Step 2
################################################################################

# Function to get the hyperlinks from a URL


def get_hyperlinks(url):

    # Try to open the URL and read the HTML
    try:
        # Open the URL and read the HTML
        with urllib.request.urlopen(url) as response:

            # If the response is not HTML, return an empty list
            if not response.info().get('Content-Type').startswith("text/html"):
                return []

            # Decode the HTML
            html = response.read().decode('utf-8')
    except Exception as e:
        print(e)
        return []

    # Create the HTML Parser and then Parse the HTML to get hyperlinks
    parser = HyperlinkParser()
    parser.feed(html)

    return parser.hyperlinks

################################################################################
# Step 3
################################################################################

# Function to get the hyperlinks from a URL that are within the same domain


def get_domain_hyperlinks(local_domain, url):
    clean_links = []
    for link in set(get_hyperlinks(url)):
        clean_link = None

        # If the link is a URL, check if it is within the same domain
        if re.search(HTTP_URL_PATTERN, link):
            # Parse the URL and check if the domain is the same
            url_obj = urlparse(link)
            if url_obj.netloc == local_domain:
                clean_link = link

        # If the link is not a URL, check if it is a relative link
        else:
            if link.startswith("/"):
                link = link[1:]
            elif (
                link.startswith("#")
                or link.startswith("mailto:")
                or link.startswith("tel:")
            ):
                continue
            clean_link = "https://" + local_domain + "/" + link

        if clean_link is not None:
            if clean_link.endswith("/"):
                clean_link = clean_link[:-1]
            clean_links.append(clean_link)

    # Return the list of hyperlinks that are within the same domain
    return list(set(clean_links))


################################################################################
# Step 4
################################################################################

def crawl(url, qty_limit=None):

    # Define a qty_limit to reduce the crawling size for testing/demonstration purpose
    count = 0

    # Parse the URL and get the domain
    local_domain = urlparse(url).netloc

    # Create a queue to store the URLs to crawl
    queue = deque([url])

    # Create a set to store the URLs that have already been seen (no duplicates)
    seen = set([url])

    # Create a directory to store the text files
    if not os.path.exists("text/"):
        os.mkdir("text/")

    if not os.path.exists("text/"+local_domain+"/"):
        os.mkdir("text/" + local_domain + "/")

    # Create a directory to store the csv files
    if not os.path.exists("processed"):
        os.mkdir("processed")

    # While the queue is not empty, continue crawling
    while queue:

        # Get the next URL from the queue
        url = queue.pop()
        print(url)  # for debugging and to see the progress
        count += 1
        if qty_limit and count > int(qty_limit):
            print(f"=> Reached quantity limit {qty_limit}, crawling stops")
            break

        # Try extracting the text from the link, if failed proceed with the next item in the queue
        try:
            # Save text from the url to a <url>.txt file
            with open('text/'+local_domain+'/'+url[8:].replace("/", "_") + ".txt", "w", encoding="UTF-8") as f:

                # Get the text from the URL using BeautifulSoup
                soup = BeautifulSoup(requests.get(url).text, "html.parser")

                # Get the text but remove the tags
                text = soup.get_text()

                # If the crawler gets to a page that requires JavaScript, it will stop the crawl
                if ("You need to enable JavaScript to run this app." in text):
                    print("Unable to parse page " + url +
                          " due to JavaScript being required")

                # Otherwise, write the text to the file in the text directory
                f.write(text)
        except Exception as e:
            print("Unable to parse page " + url)

        # Get the hyperlinks from the URL and add them to the queue
        for link in get_domain_hyperlinks(local_domain, url):
            if link not in seen:
                queue.append(link)
                seen.add(link)


################################################################################
# Step 5
################################################################################

def remove_newlines(serie):
    serie = serie.str.replace('\n', ' ', regex=True)
    serie = serie.str.replace('\\n', ' ', regex=True)
    serie = serie.str.replace('  ', ' ', regex=True)
    serie = serie.str.replace('  ', ' ', regex=True)
    return serie


################################################################################
# Step 6
################################################################################


def setup_crawler(domain, full_url, scraped_csv_filename, limit=None):

    if not domain:
        domain = "openai.com"
    if not full_url:
        full_url = "https://openai.com/"
    if not scraped_csv_filename:
        scraped_csv_filename = f"processed/{date.today()}/scraped.csv"

    print(f"{'='*20}Your cawler confirmation{'='*20}")
    print(f"domain: {domain}")
    print(f"full_url: {full_url}")
    print(f"scraped_csv_filename: {scraped_csv_filename}")
    print(f"number of url limit: {limit}")
    print()

    # Added qty limit parameter to restrict the crawling size
    print(f"Crawling Starts..")
    crawl(full_url, limit)

    # Create a list to store the text files
    texts = []

    scraped_csv_filepath, scraped_csv_filename = os.path.split(
        scraped_csv_filename)

    if not os.path.exists(scraped_csv_filepath):
        os.makedirs(scraped_csv_filepath)
        print(f"=> {scraped_csv_filepath} path created")

    scraped_csv_filepath = os.path.join(
        scraped_csv_filepath, scraped_csv_filename)

    # Get all the text files in the text directory
    for file in os.listdir("text/" + domain + "/"):

        # Open the file and read the text
        with open("text/" + domain + "/" + file, "r", encoding="UTF-8") as f:
            text = f.read()

            # Omit the first 11 lines and the last 4 lines, then replace -, _, and #update with spaces.
            texts.append(
                (file[11:-4].replace('-', ' ').replace('_', ' ').replace('#update', ''), text))

    # Create a dataframe from the list of texts
    df = pd.DataFrame(texts, columns=['fname', 'text'])

    # Set the text column to be the raw text with the newlines removed
    df['text'] = df.fname + ". " + remove_newlines(df.text)
    df.to_csv(scraped_csv_filepath)
    print(f"{'='*20}Succeed{'='*20}")
    print(f"=> {scraped_csv_filepath} has been created.")


if __name__ == "__main__":
    # Check for the function name argument
    if len(sys.argv) != 6:
        print("Usage: python3 crawler.py <function_name> <domain> <full_url> <scraped_csv_filename> <limit>")
        sys.exit(1)

    function_name = sys.argv[1]
    domain = sys.argv[2]
    full_url = sys.argv[3]
    scraped_csv_filename = sys.argv[4]
    limit = sys.argv[5]

    # Check if the specified function exists
    if function_name == "setup_crawler":
        try:
            setup_crawler(domain, full_url, scraped_csv_filename, limit)
        except Exception as e:
            print("An error occurred: " + str(e), "error")
    else:
        print(f"Function '{function_name}' not found.")
