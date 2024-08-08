from models.testapi import fetch_resume_id_api, fetch_resume_num_api, fetch_resume_profile_api, name_and_email
import pandas as pd
import asyncio

api_rank= None

#@app.route('/fetch-using-api', methods=['POST'])
async def con_data(keywords,new_jdid):
    res_id = fetch_resume_profile_api(keywords)

    if res_id is not None:
        resume_id,candidate_ids= fetch_resume_num_api(res_id)
        name_email=name_and_email(candidate_ids)
        api_rank = fetch_resume_id_api(resume_id,name_email, new_jdid)
        api_rank= pd.DataFrame(api_rank)
              
    else:
        api_rank=pd.DataFrame()
      
    return api_rank 