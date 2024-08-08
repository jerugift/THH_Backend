import requests
from bs4 import BeautifulSoup
import json
import pandas as pd


def scrape_postjobfree(job_title, state):
    url = f"https://www.postjobfree.com/resumes?q=&n=&t={job_title.replace(' ', '+')}&d=&l={state.replace(' ', '+')}&radius=25&r=100"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    title_tags = soup.find_all('h3', attrs={'class': 'itemTitle'})

    links = ["https://www.postjobfree.com" + title_tag.a['href'] for title_tag in title_tags]

    return links

def postjob_scrap(data):
    data_list = [data]
    datas = json.dumps(data_list)  # Convert the list to a JSON string
    data2 = json.loads(datas)
    for idx, condition in enumerate(data2, start=1):
        # Check if condition is a dictionary
        if isinstance(condition, dict):
            print("yes its dict")
            job_title = condition.get('job_title', '') if condition.get('job_title') else condition.get('must_have')[0] or condition.get('must_have')
            state = condition.get('locations', [''])[0] if condition.get('locations') else ''

            links_postfree = scrape_postjobfree(job_title, state)
            links_df_postfree = pd.DataFrame({'ID': [idx] * len(links_postfree), 'links': links_postfree})

            # Append to the all_links_df_postfree DataFrame
            all_links_df_postfree = pd.concat([all_links_df_postfree, links_df_postfree], ignore_index=True)
            print(all_links_df_postfree)
            return all_links_df_postfree
        else:
            print(f"Expected dictionary, but got {type(condition)}")
            continue