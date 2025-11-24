import numpy as np
import pandas as pd
import os
import re
import json
import time
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from journal_config import *

d_journal_doi = JOURNAL_DOI
d_journal_id = JOURNAL_ID

def extract_wiley_issue_html(journal_name, publication_year, base_url="https://onlinelibrary.wiley.com/loi/"):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(
            base_url+d_journal_id[journal_name] +"/year/" + str(publication_year), 
            wait_until='domcontentloaded'
        )
        page.wait_for_timeout(1000)
        html_content = page.content()
        browser.close()
    return html_content

def parse_wiley_issue_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    visitable_elements = soup.find_all('a', class_='visitable')
    volume_urls = [ve.get('href') for ve in visitable_elements]
    return volume_urls

def extract_wiley_html(append_url, base_url="https://onlinelibrary.wiley.com"):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(
            base_url+append_url, 
            wait_until='domcontentloaded'
        )
        page.wait_for_timeout(1000)
        html_content = page.content()
        browser.close()
    return html_content

def parse_wiley_volume_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    visitable_elements = soup.find_all('a', class_='visitable')
    paper_urls = [ve.get('href') for ve in visitable_elements]
    return paper_urls

def parse_wiley_metadata(html_content, journal_name, paper_number):

    # with open(html_file, 'r', encoding='utf-8') as f:
    #     html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')

    metadata = {
        'author': [],
        'title': None,
        'publication_year': None,
        'journal_name': None,
        'doi': None,
        'abstract': '',
    }

    try:
        metadata['title'] = soup.find('meta', {'name': 'citation_title'}).get('content')
        metadata['author'] = soup.find('meta', {'name': 'citation_author'}).get('content')
        metadata['publication_year'] = soup.find('span', class_='epub-date').get_text()
        metadata['journal_name'] = journal_name
        metadata['doi'] = paper_number
        metadata['abstract'] = soup.find('div', {'class': re.compile(r'abstract')}).get_text(strip=True)
        print(metadata['doi'] + " paper: " + metadata['publication_year'][-4:] + " " + metadata['title'] + " - " + metadata['author'])
    except:
        print(metadata['doi'] + "ERROR: " + metadata['title'])

    return metadata

if __name__ == "__main__":
    
    start = time.perf_counter()

    df_metadata = pd.DataFrame(columns=[
        'title',
        'author',
        'publication_year',
        'journal_name',
        'doi',
        'abstract'
    ])
    
    for j in d_journal_doi.keys():
        
        print(j)
        volume_urls = []
        paper_urls = []
        paper_volumes = []
        
        for i in range(2015, 2026):
            print(">>"+ str(i))
            while True:
                try:
                    volume_urls+=(parse_wiley_issue_html(extract_wiley_issue_html(j, i)))
                    break
                except Exception as e:
                    print(e)
        (pd.DataFrame(volume_urls, columns=["volume_urls"])).to_csv(j+'_volume_urls.csv', index=False)

        for v in volume_urls:
            print(">>>>"+v[-10:])
            while True:
                try:
                    paper_urls+= parse_wiley_volume_html(extract_wiley_html(v))
                    paper_volumes.append([paper_urls[-1], v])
                    break
                except Exception as e:
                    print(e) 
        (pd.DataFrame(paper_urls, columns=["paper_urls"])).to_csv(j+'_paper_urls.csv', index=False)
        (pd.DataFrame(paper_volumes)).to_csv(j+'_paper_volumes.csv', index=False)

        for p in paper_urls:
            try:
                metadata = parse_wiley_metadata(extract_wiley_html(p), j, p)
                df_metadata = pd.concat([df_metadata, pd.DataFrame([metadata])], ignore_index=True)
            except:
                pass
        df_metadata.to_csv(j+'.csv', index=False)

    end = time.perf_counter()
    print(f"Elapsed time: {end - start:.6f} seconds")