import requests
import pandas as pd
from sentence_transformers import SentenceTransformer, util
from models.sql import sql_data_push    
from flask import jsonify

def access_tokens():
    with open("refresh_tokens.txt","r") as token:
        token=token.read()
    access_token = token
    headers = { "Authorization": f"Bearer {access_token}" }
    return headers

#1111
def fetch_resume_profile_api(kwords):

    kwords_list=[]
    kwords_list1=[mh_skills.upper() for mh_skills in kwords["Must have"]+kwords["Good to have"]] #[0:3]]

    if kwords_list1 is None:
       return jsonify({"status":"Failure", "message":"No skillsets were extracted, please change your JD"}),500
    elif len(kwords_list1)>8:
        kwords_list=kwords_list1[0:8]
    else:
        kwords_list=kwords_list1

    skillset_to_post={
    "countries": ["US"],
    "resumeCount": 50,
    "skills": kwords_list,
    "states": ["CA","TX","NJ"],
    "withinMiles": 0,
    "zipCode": ""
    }
    #"states":["AK", "AL", "AR", "AS", "AZ", "CA", "CO", "CT", "DC", "DE", "FL", "GA", "GU", "HI", "IA", "ID", "IL", "IN", "KS", "KY", "LA", "MA", "MD", "ME", "MH", "MI", "MN", "MO", "MP", "MS", "MT", "NC", "ND", "NE", "NH", "NJ", "NM", "NV", "NY", "OH", "OK", "OR", "PA", "PR", "RI", "SC", "SD", "TN", "TX", "UT", "VA", "VI", "VT", "WA", "WI", "WV", "WY", "AK", "AL", "AR", "AS", "AZ", "CA", "CO", "CT", "DC", "DE", "FL", "GA", "GU", "HI", "IA", "ID", "IL", "IN", "KS", "KY", "LA", "MA", "MD", "ME", "MH", "MI", "MN", "MO", "MP", "MS", "MT", "NC", "ND", "NE", "NH", "NJ", "NM", "NV", "NY", "OH", "OK", "OR", "PA", "PR", "RI", "SC", "SD", "TN", "TX", "UT", "VA", "VI", "VT", "WA", "WI", "WV", "WY", "AK", "AL", "AR", "AS", "AZ", "CA", "CO", "CT", "DC", "DE", "FL", "GA", "GU", "HI", "IA", "ID", "IL", "IN", "KS", "KY", "LA", "MA", "MD", "ME", "MH", "MI", "MN", "MO", "MP", "MS", "MT", "NC", "ND", "NE", "NH", "NJ", "NM", "NV", "NY", "OH", "OK", "OR", "PA", "PR", "RI", "SC", "SD", "TN", "TX", "UT", "VA", "VI", "VT", "WA", "WI", "WV", "WY"]

    fetch_cand_prof_url="https://api.jobdiva.com/apiv2/jobdiva/TalentSearch"
    headers = access_tokens()
    response1=requests.post(fetch_cand_prof_url,headers=headers, json=skillset_to_post)

    if response1.status_code == 200:        
        data = response1.json()       
        if data is None:
            return jsonify({"status":"Failure", "message":"No resumes found, please edit your Job Description"}), 400
        else:
            return data
    else:
        print(f"Error: First API request failed with status code {response1.status_code}")



#2222

def fetch_resume_num_api(cand_json):  
    candi_id=""

    if len(cand_json) == 1:
        candi_id+="candidateIds="+str(cand_json[0]['CANDIDATEID'])
    else:    
        for ind in range(len(cand_json)-1):
            candi_id+="candidateIds="+str(cand_json[ind]['CANDIDATEID'])+"&"   
    
    resume_id_url="https://api.jobdiva.com/api/bi/CandidatesResumesDetail?"+candi_id+"alternateFormat=true"        
    headers = access_tokens()
    response2 = requests.get(resume_id_url, headers=headers)

    if response2.status_code == 200:
        resume_ids_det = response2.json()
        return resume_ids_det, candi_id
    else:
        print(f"Error: Second API request failed with status code {response2.status_code}")    

#3333   
def name_and_email(candi_id):
    cand_name_email={}

    name_email_url="https://api.jobdiva.com/api/bi/CandidatesDetail?"+candi_id+"alternateFormat=true"       
    headers = access_tokens()
    response3 = requests.get(name_email_url, headers=headers)

    if response3.status_code == 200:
        name_email_det = response3.json()            
        for ind in range(len(name_email_det['data'])):
            cand_name_email[str(name_email_det['data'][ind]['ID'])]=[name_email_det['data'][ind]['FIRSTNAME']+" "+name_email_det['data'][ind]['LASTNAME'], name_email_det['data'][ind]['EMAIL'], name_email_det['data'][ind]['CELLPHONE']]    
        
        return cand_name_email
    
    else:
        return f"Error: Third API request failed with status code {response3.status_code}"


def fetch_resume_id_api(resume_ids,names_emails,job_id):   

    id_set=set([resume_ids['data'][i]['CANDIDATEID'] for i in range(1,len(resume_ids['data']))])

    resume_ids_list=[[resume_ids['data'][j]['CANDIDATEID'],resume_ids['data'][j]['RESUMEID']] for j in range(1,len(resume_ids["data"]))]
    resume_ids_list.sort()

    cand_res_id={str(resume_ids_list[j][0]):str(resume_ids_list[j][1]) for j in range(len(resume_ids_list)) if resume_ids_list[j][0] in id_set}
    result_dfs=[]

    for id,res_id in cand_res_id.items():
        resume_det_url="https://api.jobdiva.com/api/bi/ResumeDetail?resumeId="+res_id      
        headers = access_tokens()
        response4 = requests.get(resume_det_url, headers=headers)  


        if response4.status_code == 200:
            response4_json=response4.json()
            filename=response4_json['data'][1][0].strip(".pdf .docx .txt")+".txt"            
            filepath=r"downloaded_api_resumes\\"+filename

            resume_content = response4_json['data'][1][2].replace("\r\n","")              
        
            if id in names_emails.keys():  
                if names_emails[id][2] !='':
                    print(f"IFFF Mobile is ____{names_emails[id][2]}____")
                    result_df = pd.DataFrame({'JOB_ID': [job_id], 'Resume': [resume_content], 'Signature': ['API'], 'Name':[names_emails[id][0]], 'Email':[names_emails[id][1]], 'Mobile':[names_emails[id][2]]}) # 'Similarity': [similarity_percentage]})
                    result_dfs.append(result_df)          
                else:
                    print(f"ELSEEE Mobile is ____{names_emails[id][2]}____")
                    result_df = pd.DataFrame({'JOB_ID': [job_id], 'Resume': [resume_content], 'Signature': ['API'], 'Name':[names_emails[id][0]], 'Email':[names_emails[id][1]], 'Mobile':None}) # 'Similarity': [similarity_percentage]})
                    result_dfs.append(result_df)                 
        
        else:
            return f"Error: Fourth API request failed with status code {response4.status_code}"
        
    final_result_df = pd.concat(result_dfs, ignore_index=True) 
    return final_result_df

model = SentenceTransformer("paraphrase-MiniLM-L6-v2")
def rank_text(resume, job_description):
   
    resume_embedding = model.encode(resume, convert_to_tensor=True)
    job_description_embedding = model.encode(job_description, convert_to_tensor=True)
   
    percentage = util.pytorch_cos_sim(resume_embedding, job_description_embedding)
   
    return float((percentage[0][0]*100).round(decimals=2))
 
# def rank_resumes(df1,df2,job_description):   
#     final_data = pd.concat([df1, df2], ignore_index=True)
#     final_data['Similarity'] = ''
#     final_data['Similarity'] = final_data.apply(lambda row: rank_text(row['Resume'], job_description), axis=1)
#     sql_data_push(final_data)
#     return final_data

def rank_resumes(df1,job_description):  
    # final_data = pd.concat([df1], ignore_index=True)
    final_data=df1
    print("FINAL_DATAAAAAAAAAAA", final_data)
    final_data['Similarity'] = ''
    final_data['Similarity'] = final_data.apply(lambda row: rank_text(row['Resume'], job_description), axis=1)
    sql_data_push(final_data)
    print(final_data)
    return final_data