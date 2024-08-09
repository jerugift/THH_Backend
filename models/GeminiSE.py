import google.generativeai as genai
import mysql.connector as sql
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import re
import json
from models.sql import job_detail


# def extract_skills(output):
#     must_have = re.search(r'must_have: (.*)', output)
#     good_to_have = re.search(r'good_to_have: (.*)', output)
#     experiences = re.search(r'experiences: (.*)', output)
#     locations = re.search(r'locations: (.*)', output)  
    
#     must_have_skills = must_have.group(1).split(', ') if must_have else []
#     good_to_have_skills = good_to_have.group(1).split(', ') if good_to_have else []
#     experiences = experiences.group(1).split(', ') if experiences else []
#     locations = locations.group(1).split(', ') if locations else [] 

#     print("Must have", must_have.strip("[]"))
#     print("Good to have", good_to_have.strip("[]"))
#     print("Experience", experiences.strip("[]"))
#     print("Locations", locations.strip("[]"))


#     skillsets={"Must have":must_have_skills, 
#                "Good to have": good_to_have_skills,
#                "Experience": experiences,
#                "Locations": locations}
    
#     print("SKILLSSS:", skillsets)
#     #combined_skills = ' '.join(must_have_skills + good_to_have_skills + experiences + locations)

#     return skillsets

def extract_skills(output):
    job_title = re.search(r'job_title: \[(.*)\]', output)
    must_have = re.search(r'must_have: \[(.*)\]', output)
    good_to_have = re.search(r'good_to_have: \[(.*)\]', output)
    #locations = re.search(r'locations: \[(.*)\]', output)
    experiences = re.search(r'experiences: \[(.*)\]', output)

    job_title_list = job_title.group(1).split(', ') if job_title else []
    must_have_skills = [skill.strip('"') for skill in must_have.group(1).split(', ')] if must_have else []
    good_to_have_skills = [skill.strip('"') for skill in good_to_have.group(1).split(', ')] if good_to_have else []
    #locations_list = [location.strip('"') for location in locations.group(1).split(', ')] if locations else []
    experiences_list = [experience.strip('"') for experience in experiences.group(1).split(', ')] if experiences else []

    skillsets = {
        "Job Title": [job_title_list[0].strip('"')],
        "Must have": must_have_skills,
        "Good to have": good_to_have_skills,        
        "Experiences": experiences_list,
    }
    # "Locations": locations_list,

    print("SKILLSSS:", skillsets)

    return skillsets

# Configure GenerativeAI
genai.configure(api_key="AIzaSyAN5ejPtEN-ckL0ZSwAgJMYTSw2IzR5Z8o")

def generate_search_kwords(text, email, is_file=True):

    if is_file:
        with open(text, encoding='utf-8') as f:
            text = f.read()
    # Initialize the GenerativeAI model
    model = genai.GenerativeModel('gemini-pro')  # Ensure this is the correct initialization method
    
    prompt = f'''Prompt: As a Skills Analyst, your task is to extract the skillset from job descriptions for various roles. Focus only on extracting technologies, tools, and relevant skills, and exclude any additional information such as company details, job responsibilities, and benefits. Format your response with specific categories.

    Job description:
    
    Question: Python Developer
        We are seeking a passionate Python developer to join our team. Responsibilities include developing high-quality software solutions, working on data engineering problems, and using the latest technologies and tools. 

        Required skills and qualifications:
        - Strong understanding of Python programming and frameworks.
        - Experience with front-end technologies like HTML, CSS, and JavaScript.
        - Familiarity with database technologies including SQL and NoSQL.

        Preferred skills and qualifications:
        - Experience with frameworks such as Django and Flask.
        - Knowledge in data science and machine learning.
        - Familiarity with cloud platforms such as AWS and Azure.

        Experience: 
        Location: India, US

        Answer:
        job_title: ["Python Developer"]
        must_have: ["Python", "Django", "Flask", "HTML", "CSS", "JavaScript", "SQL", "NoSQL"]
        good_to_have: ["Data science", "machine learning", "AWS", "Azure"]        
        experiences: []

    
    Question: Snowflake Engineer

        Required skills and qualifications:
        - 5-10 years of IT experience with 3+ years as a Snowflake Engineer.
        - Expertise in Snowflake data modelling, ELT, Snowflake SQL, and related technologies.
        - Experience with Snowflake utilities and data migration.

        Answer:
        job_title: ["Snowflake Engineer"]
        must_have: ["Snowflake", "data modelling", "ELT", "Snowflake SQL", "Snowflake utilities", "data migration", "RDBMS", "SQL", "PL/SQL"]
        good_to_have: []        
        experiences: ["5-10"]

    Question: Java Developer

        Description:
        Join our team as a Java Developer, responsible for designing, developing, and maintaining Java applications. Key skills include Java, Spring, Hibernate, RESTful APIs, HTML, CSS, JavaScript, and Git. Experience with testing frameworks (JUnit, TestNG) and CI/CD tools (Jenkins) is essential. You will optimize performance, integrate systems, and ensure code quality. Strong problem-solving, communication skills, and python , sql are preferred.

        Qualifications:
        - 5+ years of Java development experience.

        --- instructions : 
                1. Analyse the full job description.
                2. Create a Job Title for this JD if not exists, otherwise use the existing title (e.g., Title: Java Developer).
                3. Mark required skills as must-have skills (e.g., Java, Spring, Hibernate, RESTful APIs, HTML, CSS, JavaScript, Git, testing frameworks like JUnit, TestNG, CI/CD tools like Jenkins, performance optimization, system integration, problem-solving skills, communication skills).
                4. Mark preferred skills as good-to-have (e.g., Python, SQL).                
                5. Extract the experience if mentioned in the JD (e.g., 5+ years).
                6. Provide the same type of refined answer as used in the prompt.

        Answer:
        job_title: Java Developer
        must_have: ["Java", "Spring", "Hibernate", "RESTful APIs", "JUnit", "Testing", "Jenkins"]
        good_to_have: ["Python", "SQL"]       
        experiences: ["5+"]

    Question: {text}
        Answer:


        Provide exactly 8 top skills for both must-have and good-to-have categories. If there are more than 8 skills, only include the top 8 skills. If any of the information is not available in the job description, provide an empty response. Do not exclude any other information like not mentioned, None specified.

    '''
    
    try:
        response = model.generate_content(prompt)
        response_text = response.text.replace("*", "").strip()
        print("Gemini response: ",response_text)
        result=extract_skills(response_text)
        job_id=job_detail(text, result, email)
        skills=json.dumps(result, indent=4)
        # final = json.dumps(result, indent=4)
        return skills,job_id,text
    except Exception as e:
        print(f"An error occurred: {e}")
        return None



# user_input = """
# We are looking for a results-driven VMware engineer to optimize our company's VMware network. You will be deploying VMware applications in physical and virtual environments, integrating multiple virtual servers on a single host machine, and providing VMware support.

# To ensure success as a VMware engineer, you should exhibit sound knowledge of VMware ESX and related technologies, and experience in a similar role. An accomplished VMware engineer will be someone whose expertise results in the successful integration of VMware products across multiple data centers.

# VMware Engineer Responsibilities:
# Determining business needs and evaluating existing network infrastructure and systems.
# Optimizing network hardware and software to enable VMware integration.
# Developing and deploying customized VMware solutions.
# Defining multiple virtual servers on a single host machine.
# Virtualizing Windows servers and connecting them to networks and clouds.
# Designing and implementing virtual desktop infrastructure (VDI) and enabling template management.
# Installing operating systems and service packs, as well as security patches and bug fixes.
# Troubleshooting and resolving VMware environment issues.
# Providing technical support and documenting VMware processes.
# Keeping informed of developments in VMware technologies and products.
# VMware Engineer Requirements:
# Bachelor's degree in computer science, information technology, computer programming, or similar.
# VMWare Certified Professional (VCP) preferred.
# A minimum of 2 years experience as a VMware engineer.
# Proficiency in VMware associated programs and coding languages, such as Windows Server, MS IIS, SAN architecture, WebSphere, Citrix, Python, and C++.
# Extensive knowledge of the fundamentals of VMware ESX and related technologies.
# Excellent communication and collaboration skills.
# Exceptional analytical and technical aptitude.
# Great organizational, time management, and problem-solving skills.
# Availability to resolve urgent VMware environment problems outside of business hours.
# """
# result = generate_search_query(user_input)


# Process the output to get the must-have and good-to-have skills


# must_have_skills, good_to_have_skills, experiences, locations = extract_skills(result)

# print("re")
# print("Must-have skills:", must_have_skills)
# print("Good-to-have skills:", good_to_have_skills)
# print("Experiences:", experiences)
# print("Locations:", locations)

# Combine all extracted skills into a single string
# combined_skills = ' '.join(must_have_skills + good_to_have_skills + experiences + locations)
# print(combined_skills)


# Connect to the database
# mydb = sql.connect(
#     host="localhost",
#     user="root",
#     password="root123",
#     database="antony"
# )

# cursor = mydb.cursor()

# # Execute the query to retrieve the resumes
# cursor.execute("SELECT JOB_ID, Resume FROM candidate_info WHERE Signature LIKE 'API'")
# result = cursor.fetchall()  # Fetch all rows from the executed query

# # Convert the result to a pandas DataFrame
# df = pd.DataFrame(result, columns=['JOB_ID', 'Resume'])

# # Extract the 'Resume' column as a list
# text_data = df['Resume'].tolist()
# job_ids = df['JOB_ID'].tolist()

# # Close the database connection
# cursor.close()
# mydb.close()

# model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
# resume_embeddings = model.encode(text_data)
# skillsets_embeddings = model.encode(combined_skills)

# # Assuming skillsets_embeddings and resume_embeddings are vectors
# skillsets_embeddings = skillsets_embeddings.reshape(1, -1) if skillsets_embeddings.ndim == 1 else skillsets_embeddings
# resume_embeddings = resume_embeddings.reshape(1, -1) if resume_embeddings.ndim == 1 else resume_embeddings

# # Compute the cosine similarity between the skillset embeddings and resume embeddings
# similarities = cosine_similarity(skillsets_embeddings, resume_embeddings)

# # Output the similarity percentages for each resume
# similarity_percentages = similarities[0] * 100
# for i, (job_id, resume, similarity) in enumerate(zip(job_ids, text_data, similarity_percentages)):
#     print(f"Job ID: {job_id}: {similarity:.2f}% similarity")

# # Find the index of the resume with the highest similarity
# best_match_index = similarities.argmax()

# # Output the best matching resume
# best_matching_resume = text_data[best_match_index]
# print("Best matching resume:", best_matching_resume)

