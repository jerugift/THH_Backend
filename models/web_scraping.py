import json
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import requests
import chardet
from bs4 import BeautifulSoup
import re
import random as rd
 
def fetch(url):
    response = requests.get(url)
    raw_content = response.content
    detected_encoding = chardet.detect(raw_content)['encoding']
    return raw_content.decode(detected_encoding, errors='replace')
 
def extract_content_postjobfree(link):
    html = fetch(link)
    soup = BeautifulSoup(html, 'html.parser')
    content_tags = soup.find_all('div', class_='normalText')
    return " ".join([tag.get_text() for tag in content_tags])
 
def extract_content_jobspider(link):
    html = fetch(link)
    soup = BeautifulSoup(html, 'html.parser')
    content_tags = soup.find_all('td', width='100%')
    return " ".join([tag.get_text() for tag in content_tags])
 
def extract_name(content):
    soup = BeautifulSoup(content, 'html.parser')
    first_paragraph = soup.find('p')
    if first_paragraph and first_paragraph.text.strip():
        return first_paragraph.text.strip()
   
    lines = content.split('\n')
    for line in lines:
        stripped_line = line.strip()
        if stripped_line:
            return stripped_line
    return None
 
def extract_email(content):
    emails = re.findall(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", content)
    return emails[0] if emails else None
 
def process_resume_link(link):
    if 'postjobfree' in link:
        content = extract_content_postjobfree(link)
    elif 'jobspider' in link:
        content = extract_content_jobspider(link)
    else:
        content = ""
    name = extract_name(content)
    email = extract_email(content)
    return name, content.replace("\n", ""), email
 
def scrape_jobspider(job_title, state):
    page_no = rd.randint(1, 30)
    url = f"https://www.jobspider.com/job/resume-search-results.asp/state_{state.replace(' ', '+')}/word_{job_title.replace(' ', '+')}/page_{page_no}"
    html = fetch(url)
    soup = BeautifulSoup(html, 'html.parser')
    title_tags = soup.find_all('td', attrs={'class': 'StandardRow'})
 
    links = ["https://www.jobspider.com/" + title_tag.a['href'] if title_tag.a else None for title_tag in title_tags]
    links = [link for link in links if link is not None]
 
    return links
 
def scrape_postjobfree(job_title, state):
    url = f"https://www.postjobfree.com/resumes?q=&n=&t={job_title.replace(' ', '+')}&d=&l={state.replace(' ', '+')}&radius=25&r=100"
    html = fetch(url)
    soup = BeautifulSoup(html, 'html.parser')
    title_tags = soup.find_all('h3', attrs={'class': 'itemTitle'})
 
    links = ["https://www.postjobfree.com" + title_tag.a['href'] for title_tag in title_tags]
 
    return links
 
def scrape_and_process_resumes(result):
    all_links_list = []
 
    job_title = result.get('job_title', '') if result.get('job_title') else result.get('must_have')[0] or result.get('must_have')
    state = result.get('locations', [''])[0] if result.get('locations') else ''
 
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
       
        futures.append(executor.submit(scrape_postjobfree, job_title, state))
        futures.append(executor.submit(scrape_jobspider, job_title, state))
       
        for future in futures:
            links = future.result()
            idx = futures.index(future) // 2 + 1  # idx corresponds to the index in the results list
            links_df = pd.DataFrame({'ID': [idx] * len(links), 'links': links})
            all_links_list.append(links_df)
   
    all_links = pd.concat(all_links_list).reset_index(drop=True)
 
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(process_resume_link, all_links['links']))
 
    names, contents, emails = zip(*results)
 
    result_df = pd.DataFrame({
        'Resume': contents,
        'Signature': ['Web Scrap'] * len(contents),
        'Name': names,
        'Email': emails
    })
 
    return result_df