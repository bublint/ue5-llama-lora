import requests
from bs4 import BeautifulSoup
import logging
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import re

# Set up logging configuration
logging.basicConfig(filename='unreal_docs.log', level=logging.INFO, filemode='w')

# Function to fetch the HTML content of a given URL
def fetch_page_content(url):
    try:
        options = Options()
        options.add_argument('--headless')
        driver = webdriver.Firefox(options=options)
        driver.get(url)
        time.sleep(10)
        content = driver.page_source
        driver.quit()
        return content
    except Exception as e:
        logging.error(f"Error fetching {url}: {e}")

# Function to parse the HTML content and extract the page text
def parse_html(content, url):
    soup = BeautifulSoup(content, 'html.parser')
    # print(soup) # For debugging purposes only
    body_div = soup.find("div", {"id": "maincol"})
    if not body_div:
        logging.warning(f"body div not successfully located in {url}")
    #print(body_div) # For debugging purposes only
    elements = body_div.find_all(['p', 'h1', 'h2', 'h3'])
    if not elements:
        logging.warning(f"No tags found on {url}")
        return
    # Extract the text from each paragraph and remove consecutive whitespace characters
    texts = [re.sub(r'\s+', ' ', e.get_text().strip()) for e in elements]
    return '\n\n'.join(texts) + '\n\n'

# Main function to loop through the list of page URLs, fetch and parse their content,
# extract the content, and write it to a file
def main():
    # URLs of the pages to include in the .txt file
    with open('urls.txt', 'r') as f:
        page_urls = f.read().splitlines()

    # Initialize a string to store the content
    docs_text = ''

    # Loop through the list of page URLs
    for i, url in enumerate(page_urls):
        # Log the current page being processed
        logging.info(f"Processing page {i+1}: {url}")

        # Fetch the HTML content of the page
        content = fetch_page_content(url)

        # If the content could not be fetched, continue to the next page
        if not content:
            continue

        # Parse the HTML content and extract the maincol div
        paragraphs = parse_html(content, url)

        # If the page container could not be found, continue to the next page
        if not paragraphs:
            continue

        # Append the content to the string storing all content
        docs_text += paragraphs

        print(f'Successfully parsed page {i+1}')

    # Write the content to a file
    try:
        with open('unreal_docs.txt', 'w', encoding='utf-8') as f:
            f.write(docs_text)
            logging.info(f"Successfully wrote {len(page_urls)} pages to file.")
    except OSError as e:
        logging.error(f"Error writing to file: {e}")
    
    print("Script execution completed successfully.")

if __name__ == '__main__':
    main()