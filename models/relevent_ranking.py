# import google.generativeai as genai
# import mysql.connector
 
# def db_retrieve(ID, Name):
#     try:
#         mydb = mysql.connector.connect(
#             # host="192.168.0.195",
#             host="localhost",
#             user="root",
#             database="antony",
#             password="root123",
#             port="3306",
#             auth_plugin='mysql_native_password'
#         )
#         mycursor = mydb.cursor()
#         sql = "SELECT Resume FROM candidate_info WHERE Job_ID=%s AND Name=%s;"
#         val = (ID, Name)
#         mycursor.execute(sql, val)
#         resume = mycursor.fetchone()
#         if resume:
#             resume = resume[0]  
#         sql1 = "SELECT skillset FROM job_detail WHERE Job_ID=%s;"
#         val1 = (ID,)
#         mycursor.execute(sql1, val1)
#         skillset = mycursor.fetchone()
#         if skillset:
#             skillset = skillset[0]  
 
#         return resume, skillset  
#     except mysql.connector.Error as err:
#         return f"Database Error: {err}", None
#     except Exception as e:
#         return f"Error: {e}", None
#     finally:
#         mycursor.close()
#         mydb.close()
 
 
 
# def relative_ranking(resume, skillset):
#     try:
#         # Read the prompt content from the file
#         # with open(r"promt.txt", 'r', encoding='utf-8') as prompt_file:
#         #     prompt_content = prompt_file.read()
        
#         with open(r"promt.txt", 'r', encoding='utf-8') as prompt_file:
#             prompt_content = prompt_file.read()
#         promt_template=r"D:\THH\UpdatedFile\Backend\models\Resume_Harshi T.txt"  
#         template2=r"D:\THH\THH_File\Backend\Resume_Varshini Reddy.txt"
 
#         # Create the question with the provided paths and prompt content
#         # question = f"""
#         # Sample: {prompt_content}
#         # Skillset Content: {skillset}\n
#         # Resume Content: {resume}\n
#         # Test Answer:"""
#         question = f"""
#         Sample: {prompt_content.format(prompt_resume=promt_template, utemp_resume=resume, uskillset=skillset, prompt_resume2=template2)}
#         Skillset Content: {skillset}\n
#         Resume Content: {resume}\n
#         Test Answer:"""
 
#         # Configure the generative AI model
#         genai.configure(api_key="AIzaSyDTXKlJq27fF0AiTvw7rK302TLCzNVwFQw")
#         model = genai.GenerativeModel('gemini-pro')
 
#         # Generate the content based on the question
#         response = model.generate_content(question)
#         print(response.text)
#         return response.text
#     except Exception as e:
#         return f"Error: {e}"



# import google.generativeai as genai
# import mysql.connector
# import time
 
# def db_retrieve(ID, Name):
#     try:
#         mydb = mysql.connector.connect(
#             host="localhost",
#             user="root",
#             database="Antony",
#             password="root123",
#             port="3306",
#             auth_plugin='mysql_native_password'
#         )
#         mycursor = mydb.cursor()
#         sql = "SELECT Resume FROM candidate_info WHERE Job_ID=%s AND Name=%s;"
#         val = (ID, Name)
#         mycursor.execute(sql, val)
#         resume = mycursor.fetchone()
#         if resume:
#             resume = resume[0]
#         sql1 = "SELECT skillset FROM job_detail WHERE Job_ID=%s;"
#         val1 = (ID,)
#         mycursor.execute(sql1, val1)
#         skillset = mycursor.fetchone()
#         if skillset:
#             skillset = skillset[0]
 
#         return resume, skillset
#     except mysql.connector.Error as err:
#         return f"Database Error: {err}", None
#     except Exception as e:
#         return f"Error: {e}", None
#     finally:
#         mycursor.close()  
#         mydb.close()
 
# def relative_ranking(resume, skillset):
#     try:
#         with open(r"promt3.txt", 'r', encoding='utf-8') as prompt_file:
#             prompt_content = prompt_file.read()
 
#         question = f"""
#         Sample: {prompt_content}
#         Skillset Content: {skillset}\n
#         Resume Content: {resume}\n
#         Test Answer:"""
 
#         genai.configure(api_key="AIzaSyDTXKlJq27fF0AiTvw7rK302TLCzNVwFQw")
#         model = genai.GenerativeModel('gemini-pro')
 
#         max_retries = 5
#         retry_delay = 1  # initial delay in seconds
 
#         for attempt in range(max_retries):
#             try:
#                 response = model.generate_content(question)
#                 # Truncate the response to 50 words
#                 truncated_response = ' '.join(response.text.split()[:75])
#                 print(truncated_response)
#                 return truncated_response
#             except genai.exceptions.RateLimitError:
#                 print(f"Rate limit exceeded. Retrying in {retry_delay} seconds...")
#                 time.sleep(retry_delay)
#                 retry_delay *= 2  # Exponential backoff
#             except Exception as e:
#                 return f"Error: {e}"
#         return "Error: Maximum retries exceeded. Please try again later."
#     except Exception as e:
#         return f"Error: {e}"
 
# # Example usage
# resume, skillset = db_retrieve("job_id_example", "name_example")
# output = relative_ranking(resume, skillset)
# print(output)[12:28 PM] Rohkith Roshan
 
import google.generativeai as genai
import mysql.connector
import time
from functools import lru_cache
 
# Database retrieval function
def db_retrieve(ID, Name):
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            database="antony",
            password="root123",
            port="3306",
            auth_plugin='mysql_native_password'
        )
        mycursor = mydb.cursor()
        sql = "SELECT Resume FROM candidate_info WHERE Job_ID=%s AND Name=%s;"
        val = (ID, Name)
        mycursor.execute(sql, val)
        resume = mycursor.fetchone()
        if resume:
            resume = resume[0]
        sql1 = "SELECT skillset FROM job_detail WHERE Job_ID=%s;"
        val1 = (ID,)
        mycursor.execute(sql1, val1)
        skillset = mycursor.fetchone()
        if skillset:
            skillset = skillset[0]
 
        return resume, skillset
    except mysql.connector.Error as err:
        return f"Database Error: {err}", None
    except Exception as e:
        return f"Error: {e}", None
    finally:
        mycursor.close()  
        mydb.close()
 
# Cache mechanism to store outputs for consistent responses
@lru_cache(maxsize=100)
def cached_relative_ranking(question):
    genai.configure(api_key="AIzaSyDTXKlJq27fF0AiTvw7rK302TLCzNVwFQw")
    model = genai.GenerativeModel('gemini-pro')
    max_retries = 5
    retry_delay = 0.5  # initial delay in seconds
 
    for attempt in range(max_retries):
        try:
            response = model.generate_content(question)
            truncated_response = ' '.join(response.text.split()[:70])            
            return truncated_response
        except genai.exceptions.RateLimitError:
            print(f"Rate limit exceeded. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
            retry_delay *= 2  # Exponential backoff
        except Exception as e:
            return f"Error: {e}"
    return "Error: Maximum retries exceeded. Please try again later."
 
# Function to generate relative ranking
def relative_ranking(resume, skillset):
    try:
        with open("promt3.txt", 'r', encoding='utf-8') as prompt_file:
            prompt_content = prompt_file.read()
 
        question = f"""
        Sample: {prompt_content}\n
        Skillset Content: {skillset}\n
        Resume Content: {resume}\n
        Test Answer:"""
 
        return cached_relative_ranking(question)
    except Exception as e:
        return f"Error: {e}"
 
# Example usage
# resume, skillset = db_retrieve("job_id_example", "name_example")
# output = relative_ranking(resume, skillset)
# print(output)