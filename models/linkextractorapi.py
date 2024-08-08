from flask import Flask, request, jsonify
import google.generativeai as genai
import serpapi
import mysql.connector as sql
import pandas as pd
import datetime
import re 


# Initialize df as an empty DataFrame
df = pd.DataFrame(columns=['Name', 'Link', 'Query'])
file_name = "result"

new_jdid = None


# Configure GenerativeAI
genai.configure(api_key="AIzaSyAN5ejPtEN-ckL0ZSwAgJMYTSw2IzR5Z8o")

def generate_search_query(user_input):
    # Initialize the GenerativeAI model
    model = genai.GenerativeModel('gemini-pro')
    
    response = model.generate_content(f'''Prompt: As an aspiring talent seeker, you're eager to find the perfect candidates for various roles. You've compiled a list of desired qualifications and universities. Your task is to craft Boolean search queries tailored to these criteria. Remember to focus solely on generating the search queries, excluding any additional information. Utilize LinkedIn platforms for your search.

                                      Desired Qualifications and Universities:
 
                                      Question : I need a MIT computer science graduate for python developer

                                      Answer : "MIT computer science" (software engineer OR python developer OR data scientist) site:www.linkedin.com/in
 
                                      Question :provide me data science student profiles from Harvard University in the US

                                      Answer : "data science " student Harvard University (US OR United States) site:www.linkedin.com/in
 
                                      Question : give me a undergraduate students with a passion for cybersecurity from Georgia Institute of Technology (GA) and University of Illinois Urbana-Champaign (IL)

                                      Answer : "cybersecurity" student ("Georgia Institute of Technology" OR "University of Illinois Urbana-Champaign") (US OR "United States") (club OR forum) site:www.linkedin.com/in
 
                                      Question: I need few profiles where data science is required as a skill.

                                      Answer: "data science" (required OR necessary OR must-have OR essential) site:www.linkedin.com/in
 
                                      Question: give me a technical intern profiles from pozent Labs 

                                      Answer : site:www.linkedin.com/in "company pozent Labs" "technical intern"
 
                                      Question : give me a Gen AI intern profiles from pozent Labs 

                                      Answer : site:www.linkedin.com/in "company pozent Labs" "Gen AI"
 
                                      Question :  provide me a Datascience profiles from harvard university

                                      Answer : "data science " student Harvard University (US OR United States) site:www.linkedin.com/in
 
                                      Question :  i need a bsc computer science students from gurunanak college of arts and science whose name is Nagarajan B J 

                                      Answer : "bsc computer science" student "Gurunanak College of Arts and Science" "Nagarajan B J" site:www.linkedin.com/in
 
                                      Question : Find a LinkedIn profile of a student named Easuraja A studying BSc Computer Science at the University of Madras.

                                      Answer : "bsc computer science" student "University of Madras" "Easuraja A" site:www.linkedin.com/in
 
                                      Question : give me data science profile from IIT madras

                                      Answer : "data science" student IIT Madras site:www.linkedin.com/in
 
                                      Question : give me python profile from IIT madras

                                      Answer : "python" student "IIT Madras" site:www.linkedin.com/in
 
                                      Question: provide me data science student profiles from Stanford University

                                      Answer: "data science" student Stanford University (US OR United States) site:www.linkedin.com/in
 
                                      Question: provide me data science student profiles from University of California, Berkeley

                                      Answer: "data science" student "University of California, Berkeley" (US OR United States) site:www.linkedin.com/in
 
                                      Question: provide me data science student profiles from University of Southern California

                                      Answer: "data science" student "University of Southern California" (US OR United States) site:www.linkedin.com/in
 
                                      Question: provide me data science student profiles from University of Texas at Austin

                                      Answer: "data science" student "University of Texas at Austin" (US OR United States) site:www.linkedin.com/in
 
                                      Question: provide me data science student profiles from University of Washington

                                      Answer: "data science" student "University of Washington" (US OR United States) site:www.linkedin.com/in
 
                                      Question :  i need a bsc computer science students from gurunanak college of arts and science 

                                      --- instructions : 

                                      1.Start with the academic qualification or course name enclosed in quotation marks, like: "academic qualification".

                                      2.Enclose the name of the educational institution or college in quotation marks, for example: "college name".

                                      3.Specify the name of the student enclosed in quotation marks, like: "full name".

                                      4.Specify the desired platform using the format: site:platformname.com.

                                      5.Combine all elements into a Boolean search query, for instance: "academic qualification" "college name" "full name" site:platformname.com.
 
                                      Answer : "bsc computer science" student "Gurunanak College of Arts and Science" site:www.linkedin.com/in
 
                                      

                                      Question : {user_input}

                                      Answer : 

                                      Modify this prompt to create a Boolean search query. Provide only the search query, excluding any additional details. Use sites as LinkedIn.

                                      ''')
    
    response_text = response.text.replace("*", "").strip()
    return response_text

def search_google(query, num_results, api_keys):
    for api_key in api_keys:
        params = {
            "api_key": api_key,
            "q": query,
            "engine": "google",
            "num": num_results
        }
        try:
            results = serpapi.search(params)
            if results.get("search_metadata"):
                return results
        except Exception as e:
            continue
    return {"error": "All API keys failed"}

def save_to_database(df, user_email,boolean_query):
# def save_to_database(name, link, user_query,user_email,timestamp):
    global new_jdid

    db = sql.connect(
        #host="192.168.0.195",
        host="localhost",
        user="root",
        password="root123",
        database="antony"
    )
    cursor = db.cursor()
    
    cursor.execute(f"SELECT MAX(job_id) FROM link_extractor where email='{user_email}'")
    result = cursor.fetchone()
    
    max_id = result[0]
    if max_id==None:
        #max_id=100        
        #new_jdid = f'Job id:{max_id + 1}'
        new_jdid = 'Job id_LE:101'
    else:
        jdid=int(max_id[10:])+1
        new_jdid=f'Job id_LE:{jdid}'
    print(new_jdid)
    for index, row in df.iterrows():
        sql_query = "INSERT INTO link_extractor (job_id, name, link, jd, Event_Timestamp, email,Booleanquery) VALUES (%s, %s, %s, %s, %s,%s,%s)"
        sql_values = (new_jdid, row['Name'], row['Link'], row['Query'], row['Timestamp'], row['Email'], boolean_query)
        cursor.execute(sql_query, sql_values)
    db.commit()
    return new_jdid

# @app.route('/download-csv', methods=['GET'])
# def download_csv():
#     global file_name
#     #file_name = request.args.get('file_name',{file_name})
#     csv = df.to_csv(index=False)
#     response = app.response_class(
#         response=csv,
#         mimetype='text/csv',
#         headers={
#             'Content-Disposition': f'attachment;filename={file_name}.csv',
#             'Content-Type': 'application/octet-stream'
#         }
#     )
#     print(response)
#     return response

# if __name__ == "__main__":
#     app.run(debug=True)



#1.http://127.0.0.1:5000/search - body{json}

# {
#   "user_input": "I need a MIT computer science graduate for python developer",
#   "email": "raja@devpozent.com",
#   "file_name": "datascience"
# }


#2.http://127.0.0.1:5000/download-csv
