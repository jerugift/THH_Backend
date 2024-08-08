from flask import request, jsonify
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import re


# Define global variable for keywords_result
keywords_result = [...]

# Define your content extraction functions
def extract_content_postjobfree(link):
    response = requests.get(link)
    soup = BeautifulSoup(response.content, 'html.parser')
    content_tags = soup.find_all('div', class_='normalText')
    return "Extracted content from postjobfree"

def extract_content_jobspider(link):
    response = requests.get(link)
    soup = BeautifulSoup(response.content, 'html.parser')
    content_tags = soup.find_all('td', width='100%')
    return "Extracted content from jobspider"

def remove_empty_lines(text):
    return re.sub(r"^/s*$","",text,flags=re.MULTILINE)

# Define your relative ranking function
def relative_ranking(resume_path, skillset_path, promt):
    try:
        
        with open(promt, 'r', encoding='utf-8' ) as promts:
            promt_content= promts.read()

        question = f"""
            Sample: {promt_content}
            Skillset Content: {skillset_path}\n
            Resume Content: {resume_path}\n
            Test Answer:"""
        questions=remove_empty_lines(question)
            
        genai.configure(api_key="AIzaSyDTXKlJq27fF0AiTvw7rK302TLCzNVwFQw")
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(questions)
        print(response.text)
        return response.text
    except Exception as e:
        return f"Error: {e}"
