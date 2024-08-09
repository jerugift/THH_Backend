from flask import Flask, request, jsonify, redirect, url_for
import json
import spacy
import os
import re
import datetime
import requests
import tempfile
import logging
import pandas as pd
import bcrypt 
import jwt
import datetime
from flask_sqlalchemy import SQLAlchemy
import mysql.connector as sql
from flask_cors import CORS
from models.web_scraping import scrape_and_process_resumes
from models.api_jobdiva import con_data
from models.testapi import rank_resumes
from models.func_db import create_tables_if_not_exist
from models.testflas import get_user_role_and_jobs
from models.nlp import chat_with_sql
from models.keywords_ import extract_keywords_and_save
from models.testmail import Trigger
from models.relevent_ranking import relative_ranking,db_retrieve
from models.sql import common_dash_func, rel_rank
from models.downapi import download_api_resumes
from models.linkextractorapi import generate_search_query, search_google, save_to_database
from models.filterdownloadapi import connect_to_database
from models.GeminiSE import generate_search_kwords

 
app = Flask(__name__)
CORS(app)

global_result ={}

keywords_result = [...]
df = pd.DataFrame(columns=['Name', 'Link', 'Query'])
file_name = "result"
final_job_id=None

connection = sql.connect(
        user="root",
        host="localhost",
        database="antony",
        password="root123",
        port="3306",
        auth_plugin='mysql_native_password'
    )
cursor = connection.cursor()
create_tables_if_not_exist(cursor)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root123@localhost:3306/antony'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'tucEDtE44BbQLv7tXCivZkn1DbmKGsYb'

 
nlp = spacy.load("model-best")
 
result_df=None
api_rank=None

db = SQLAlchemy(app)

class UserInfo(db.Model):
    __tablename__ = 'user_info'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    Role = db.Column(db.String(50), nullable=False)  # Add role column

    def __repr__(self):
        return f'<UserInfo {self.username}>'
    
    # !     JWT TOKEN GENERATE FUNCTION
# def generate_token(user):
#     token = jwt.encode({
#         'user_id': user.id,
#         'username': user.username,
#         'email': user.email,
#         'role': user.Role,  # Include user's role
#         'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
#     }, app.config['SECRET_KEY'], algorithm='HS256')
#     return token
def generate_token(user):
    payload = {
        'user_id': user.id,
        'username': user.username,
        'email': user.email,
        'role': user.Role,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=12)
    }
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    return token  # Directly return the token as string


# *             USER SIGNUP API

# @app.route('/user/signup', methods=['POST'])
# def signup():
#     data = request.json
#     username = data.get('username')
#     email = data.get('email')
#     password = data.get('password')
    
#     if not username or not email or not password:
#         return jsonify({"error": "Missing username, email, or password"}), 400
    
#     if UserInfo.query.filter_by(username=username).first() is not None:
#         return jsonify({"error": "Username already exists"}), 409
    
#     # Hash the password before storing it
#     hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
#     new_user = UserInfo(username=username, email=email, password=hashed_password,Role='user')
#     db.session.add(new_user)
#     db.session.commit()
#     # !     TOKEN GENERATE
#     token = generate_token(new_user)

#     return jsonify({"message": "Success", "token": token}), 200
@app.route('/user/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not username or not email or not password:
        return jsonify({"error": "Missing username, email, or password"}), 400
    
    if UserInfo.query.filter_by(username=username).first() is not None:
        return jsonify({"error": "Username already exists"}), 409
    
    if UserInfo.query.filter_by(email=email).first() is not None:
        return jsonify({"error": "Email already exists"}), 409

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).strip().decode('utf-8')
    
    new_user = UserInfo(username=username, email=email, password=hashed_password, Role='user')
    db.session.add(new_user)
    db.session.commit()

    token = generate_token(new_user)
    return jsonify({"message": "Success", "token": token}), 200

# !correct one
# @app.route('/user/signin', methods=['POST'])
# def signin():
#     data = request.json
#     username = data.get('username')
#     password = data.get('password')
    
#     if not username or not password:
#         return jsonify({"status": "Failure", "message": "Missing username or password"}), 400
    
#     user = UserInfo.query.filter_by(username=username).first()
#     if not user:
#         return jsonify({"status": "Failure", "message": "User not found"}), 404
    
#     if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
#         token = generate_token(user)
#         return jsonify({"status": "Success", "message": "Sign in successful", "token": token}), 200
#     else:
#         return jsonify({"status": "Failure", "message": "Invalid password"}), 401
    
@app.route('/user/signin', methods=['POST'])
def signin():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"status": "Failure", "message": "Missing username or password"}), 400
    
    user = UserInfo.query.filter_by(username=username).first()
    if not user:
        return jsonify({"status": "Failure", "message": "User not found"}), 404
    
    if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        token = generate_token(user)
        return jsonify({"status": "Success", "message": "Sign in successful", "token": token}), 200
    else:
        return jsonify({"status": "Failure", "message": "Invalid password"}), 401


@app.route('/user/changepass', methods=['POST'])
def forgot_password():
    data = request.json
    email = data.get('email')
    new_password = data.get('newPassword')
    confirm_password = data.get('confirmPassword')
    
    if not email or not new_password or not confirm_password:
        return jsonify({"error": "Missing email, new password, or confirm password"}), 400
    
    if new_password != confirm_password:
        return jsonify({"error": "Passwords do not match"}), 400
    
    user = UserInfo.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    user.password = hashed_password
    db.session.commit()
    
    return jsonify({"message": "Password updated successfully"}), 200

# !correct one
# @app.route('/user/auth', methods=['GET'])
# def auth():
#     auth_header = request.headers.get('Authorization')
#     if auth_header:
#         token = auth_header.split(" ")[1]
#         try:
#             decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
#             return jsonify({"status": "Success", "data": decoded}), 200
#         except jwt.ExpiredSignatureError:
#             return jsonify({"status": "Failure", "message": "Token expired"}), 401
#         except jwt.InvalidTokenError:
#             return jsonify({"status": "Failure", "message": "Invalid token"}), 401
#     else:
#         return jsonify({"status": "Failure", "message": "Token is missing"}), 401
    
# logging.basicConfig(level=logging.DEBUG)

# try:
#     with open(r'D:\THH\THH_File\Backend\conversation_tree.json', 'r') as file:
#         conversation_tree = json.load(file)
# except Exception as e:
#     logging.error(f"Error loading conversation_tree.json: {e}")
#     conversation_tree = {}

# current_node = "start"

@app.route('/user/auth', methods=['GET'])
def auth():
    auth_header = request.headers.get('Authorization')
    if auth_header:
        try:
            token = auth_header.split(" ")[1]
            decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            return jsonify({"status": "Success", "data": decoded}), 200
        except jwt.ExpiredSignatureError:
            return jsonify({"status": "Failure", "message": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"status": "Failure", "message": "Invalid token"}), 401
    else:
        return jsonify({"status": "Failure", "message": "Token is missing"}), 401

# Logging setup
# logging.basicConfig(level=logging.DEBUG)

# try:
#     with open(r'D:\THH\THH_File\Backend\conversation_tree.json', 'r') as file:
#         conversation_tree = json.load(file)
# except Exception as e:
#     logging.error(f"Error loading conversation_tree.json: {e}")
#     conversation_tree = {}

# current_node = "start"


# @app.route('/response', methods=['POST'])
# def get_response():
#     global current_node
#     try:
#         response_text = request.json.get('message')
#         if not response_text:
#             raise ValueError("No response message provided")

#         logging.debug(f"Received message: {response_text}")

#         if current_node in conversation_tree:
#             options = conversation_tree[current_node][1]
#             if response_text.lower() in options:
#                 next_node = options[response_text.lower()]
#                 if next_node is not None:
#                     if next_node == "start":
#                         current_node = "start"
#                     elif next_node in ["e", "f"]:
#                         current_node = next_node
#                     else:
#                         current_node = next_node
#                     next_message = conversation_tree[current_node][0]
#                 else:
#                     current_node = "start"
#                     next_message = "Your Folder Have been Successfully Uploaded Wait for Sometime While We Scrap The Finest Candidates...."
#             elif current_node == "NLP":
#                 next_message = chat_with_sql(response_text)
#             else:
#                 next_message = "Invalid response to continue \n A: Talent Resourcing \n B: Deep-Doc-Verify \n C: Link Extraction \n D: Chat with Database"
#         else:
#             next_message = "Invalid conversation node."

#         logging.debug(f"Next message: {next_message}")
#         return jsonify({'message': next_message})
    
#     except Exception as e:
#         logging.error(f"Error processing response: {e}")
#         return jsonify({"status":"Failiure",'message': str(e)}), 500
    
@app.route('/response', methods=['POST'])
def get_response():
    global current_node
    try:
        response_text = request.json.get('message')
        if not response_text:
            raise ValueError("No response message provided")

        logging.debug(f"Received message: {response_text}")

        if current_node in conversation_tree:
            options = conversation_tree[current_node][1]
            if response_text.lower() in options:
                next_node = options[response_text.lower()]
                if next_node is not None:
                    if next_node == "start":
                        current_node = "start"
                    elif next_node in ["e", "f"]:
                        current_node = next_node
                    else:
                        current_node = next_node
                    next_message = conversation_tree[current_node][0]
                else:
                    current_node = "start"
                    next_message = "Your Folder Have been Successfully Uploaded Wait for Sometime While We Scrap The Finest Candidates...."
            elif current_node == "NLP":
                next_message = chat_with_sql(response_text)
            else:
                next_message = "Invalid response to continue \n A: Talent Resourcing \n B: Deep-Doc-Verify \n C: Link Extraction \n D: Chat with Database"
        else:
            next_message = "Invalid conversation node."

        logging.debug(f"Next message: {next_message}")
        return jsonify({'message': next_message})
    
    except Exception as e:
        logging.error(f"Error processing response: {e}")
        return jsonify({"status": "Failure", 'message': str(e)}), 500

# Logging setup
logging.basicConfig(level=logging.DEBUG)

try:
    with open('conversation_tree.json', 'r') as file:
        conversation_tree = json.load(file)
except Exception as e:
    logging.error(f"Error loading conversation_tree.json: {e}")
    conversation_tree = {}

current_node = "start"
@app.route('/get-job-details', methods=['GET'])
def get_job_details():
    email = request.args.get('email')
    # table = request.args.get('fetch_resume')
    table='candidate_info'
    if not email:
        return jsonify({"status":"Failure","message": "Email parameter is missing"}),400
    
    
    return get_user_role_and_jobs(email,table)


@app.route('/get-link-details', methods=['GET'])
def get_link_details():
    email = request.args.get('email')    
    table='link_extractor'
    if not email:
        return jsonify({"status":"Failure","message": "Email parameter is missing"}),400
    
    return get_user_role_and_jobs(email,table)


@app.route('/get-validation-details', methods=['GET'])
def get_validation_details():
    email = request.args.get('email')
    table='validation'
    if not email:
        return jsonify({"status":"Failure","message": "Email parameter is missing"}),400
    
    return get_user_role_and_jobs(email,table)
    

@app.route('/extract_keywords', methods=['POST'])
def extract_keywords():
    email = request.form.get('email')
    text = request.form.get('text')
    file = request.files.get('file')
    print(file, text, email)
 
    if not email:
        return jsonify({'status': 'Failure', 'message': 'No email provided'}), 400
 
    if text and not file:
        results, job_id,text = generate_search_kwords(text, email, is_file=False)
        print(results)
        return redirect(url_for('final_con', results=results, job_id=str(job_id),text=str(text)))
    elif file:
        if file.filename == '':
            return jsonify({'status': 'Failure', 'message': 'No selected file'}), 400
 
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            file.save(temp_file.name)
            temp_path = temp_file.name
 
        results, job_id,text = generate_search_kwords(temp_path, email)
        os.remove(temp_path)
        print("1111111111111",results)
        print(type(results))
        # scrape_postjob = postjob_scrap(results)
        #return redirect(url_for('scrape_and_get_links', results=results, job_id=str(job_id),text=str(text)))#, scrape_postjob=scrape_postjob
        return redirect(url_for('final_con', results=results, job_id=str(job_id),text=str(text)))
    else:
        return jsonify({'status': 'Failure', 'message': 'No text or file provided'}), 400
 
async def main(keyword,jd_id):
    data = await con_data(keyword,jd_id)
    return data
   
 
@app.route('/fetch-using-api', methods=['GET'])
async def final_con():
    global api_rank
    global final_job_id
    text = request.args.get('text')
    data = request.args.get('results')
    data = data.replace("'", '"')
    print(data)
    job_id = request.args.get('job_id')
    print('66666',job_id)
    results = json.loads(data)
    print(results)
   
    final_job_id=job_id
 
    try:
        final_api_rank = await main(data, job_id)
        api_rank = pd.DataFrame(final_api_rank)
        # if api_rank is not None:
        return redirect(url_for('rank',text=text))
        # else:
        #     return jsonify({"status":"Failure", "message":"No resumes found, please edit your Job Description"}), 400
 
    except Exception as e:
        return jsonify({"status": "Error", "message": str(e)}), 500
 
@app.route('/Ranking', methods=['GET'])
def rank():
    global api_rank
    global result_df
    global final_job_id
    data = request.args
    job_description = data.get('text')
    #print(result_df['JOB_ID'])
    #rank_resumes(api_rank, result_df, job_description)
    rank_resumes(api_rank, job_description)
    return jsonify({"status": "Success", "message":f"Your resumes have been fetched. Click {final_job_id} in the dashboard to view your resumes"}),200
 

@app.route('/download_api_resumes', methods=['GET'])
def download_api_resumes_route():
    email_id = request.args.get('email')
    jd_id = request.args.get('jd_id')
    if not email_id:
        return jsonify({"message": "Email ID is required", "data": []})
    
    return download_api_resumes(email_id, jd_id)


#Endpoint to send Email to candidates
@app.route('/send-invitation', methods=['POST'])
def send_invitation():
    candidate_email = request.args.get('email')
    candidate_name = request.args.get('name')
    #availability_datetime = request.args.get('availability_datetime')

    if not candidate_email or not candidate_name: #or not availability_datetime:
        return jsonify({'error': 'Missing required fields'}), 400

    result = Trigger(candidate_email, candidate_name) #, availability_datetime)
    if isinstance(result, dict):
        return jsonify(result), 500
    else:
        return jsonify({'message': result}), 200
    
#Endpoint to process Relative Ranking
@app.route('/Relevant', methods=['POST'])
def Relevant():
    try:
        name = request.args.get('name')
        job_id = request.args.get('job_id')
        resume, skillset = db_retrieve(job_id, name)
        if not resume or not skillset:
            return jsonify({"status":"Failure",'message': 'Error retrieving resume or skillset'}), 500
        result = relative_ranking(resume, skillset)
        db_save=rel_rank(job_id, name, result)
        print(db_save)
        return jsonify({"status":"Success",'relevent_experience': result}),200
    except Exception as e:
        return jsonify({"status":"Failure",'message': f"Error: {e}"}), 500
    

@app.route('/search', methods=['POST'])
def search():
    global df
    global file_name  # Accessing the global variable df
    le_jdid=None
    data = request.json
    user_input = data.get('user_input')
    num_results = 300  # Default to 300 results
    file_name = data.get('file_name')
    user_email = data.get("email")

    boolean_query = generate_search_query(user_input)
    api_keys = [
        "ea07a3c37f690319b935d3d544d9569357871e77075e98a1a453a4b84b0e6958",
            "1c31b579bef73a71c97ed83d9daa5c2548eb91687a63bb771749b20034e41fd5",
            "fc37e93a1819bd6f9f164d737e74579deaff8026f9415f02fed3eed2aa2f7cad",
            "d7d7ee684726b9d7c3cc270be8377c23eba0c5328bb9273ede1ef24ee3284cbf",
            "547105fc3151874c26a09dfbc32fbac6dc3ae999a55516d6333816aefebb1f27",
            "e21f059fec89d8e49a2053ae67955ce892a81f091c018be65ad54d02bffd60fe",
            "754e0b31534e16625470fd1c9bfc02387f5c6f4c7846e686fedbbd59e51b2e90",
            "4744a35061a0be80d2cda9730ed4b7d1cae93652bda6f6cc945d150ae40ebf3c",
            "851c0521790a60e6756c669cb64444e5725f48a8d7946ab3507e88b949f985b0",
            "1f197df48d7ea0a42278c0e3d73da7f57bccd6bb671bf1f4168119ff853663c6",
            "75721bc7a9e2622abfdd979de405c016e9f0e8652516e7a66b56828e2e0f3f34"
    ]
    results = search_google(boolean_query, num_results, api_keys)
    df_list=[]
    if "error" not in results:
        if "organic_results" in results:
            for result in results["organic_results"]:
                name = result.get('title', '')
                link = result.get('link', '')
                if re.match(r"https://(www|in|uk|us|ca|au|fr|de|es|it|cn|jp|br|mx|sg|nz|za|ae|sa|hk|my|id|th|ph|vn|kr|tw|se|no|fi|dk|nl|be|ch|at|pl|cz|hu|tr|il|ru|ie|pt|gr)\.linkedin\.com/in/.*", link):
                    timestamp = datetime.datetime.now()
                    df_list.append(pd.DataFrame({'Name': [name], 'Link': [link], 'Query': [user_input],'Email':[user_email],'Timestamp':[timestamp]}))
                    
            if df is not None:
                df = pd.concat(df_list, ignore_index=True)
                print(df)
                #save_to_database(name, link, user_input,user_email,timestamp)
                le_jdid= save_to_database(df, user_email,boolean_query)
            else:
                return jsonify({"message": "No results fetched, please modify your prompt",}), 406

    if le_jdid is not None:
        return jsonify({"message": f"Search completed. Please check {le_jdid} in the dashboard to view the results. \nWhat else would you like to do: \nA: Talent Resourcing\nB: Deep-Doc-Verify\nC: Link Extraction\nD: Chat with Database", "results": df.to_dict(orient='records')}), 200
    else:
        return jsonify({"message": "Search completed, but no results have been found. Please optimize your query. \nWhat else would you like to do: \nA: Talent Resourcing\nB: Deep-Doc-Verify\nC: Link Extraction\nD: Chat with Database", "results": df.to_dict(orient='records')}), 200

@app.route('/download_links', methods=['GET'])
def download_links():
    #filters = request.json.get('filters', {})
    job_id = request.args.get('job_id')
    email = request.args.get('email')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
 
    file_name="LE_Resume"
    date_filter = ""
    params = []
 
    if start_date:
        start_date += " 00:00:00"
        date_filter += "AND (Event_Timestamp >= %s) "
        params.append(start_date)
 
    if end_date:
        end_date += " 23:59:59"
        date_filter += "AND (Event_Timestamp <= %s) "
        params.append(end_date)
 
    query = f"""
        SELECT *
        FROM link_extractor
        WHERE
            (Job_Id = %s OR %s IS NULL OR %s = '')
            AND (Email = %s OR %s IS NULL OR %s = '')
            {date_filter}
    """
 
    params = [job_id, job_id, job_id, email, email, email] + params
    query = query.format(timestamp_field="Event_Timestamp")
 
    try:
        connection = connect_to_database()
        if connection is None:
            return jsonify({"status": "failure", "message": "Database connection failed"}), 500
 
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params)
        result = pd.DataFrame(cursor.fetchall())
        print(result)
 
        csv = result.to_csv(index=True)
        response = app.response_class(
            response=csv,
            mimetype='text/csv',
            headers={
                'Content-Disposition': f'attachment;filename={file_name}.csv',
                'Content-Type': 'application/octet-stream'
            }
        )
        print(response)
        #return response        
 
        cursor.close()
        connection.close()
       
        response.headers['Success-Message'] = 'File downloaded successfully'
        return response, 200              
        #return jsonify({"status": "Success", "message": "File downloaded successfully"}), 200
   
    except sql.Error as error:
        print("Error executing query:", error)
        return jsonify({"status": "failure", "message": "Error executing query", "error": str(error)}), 500


@app.route('/fetch_candidates', methods=['POST'])
def fetch_candidates_by_filters():
    filters = request.json.get('filters', {})
    print(filters)
    # table = request.json.get('fetch_resume')
    table = 'candidate_info'
    return common_dash_func(filters,table)


@app.route('/link_extracting', methods=['POST'])
def fetch_links_by_filters():
    filters = request.json.get('filters', {})
    print(filters)    
    table =  'link_extractor'
    return common_dash_func(filters,table)


@app.route('/data_validation', methods=['POST'])
def fetch_validation_by_filters():
    filters = request.json.get('filters', {})
    print(filters)    
    table = 'validation'
    return common_dash_func(filters,table)

 

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
 
 
@app.route('/docvalidation', methods=['POST'])
def test_api_predict():
    url="https://fc66-35-188-239-217.ngrok-free.app/predict"
 
    if 'file' not in request.files:
        return jsonify({"status": "failure", "message": "No file part"}), 400
 
    file = request.files['file']
    print(file)
 
    if file.filename == '':
        return jsonify({"status": "failure", "message": "No selected file"}), 400
   
    if not allowed_file(file.filename):
        return jsonify({"status": "failure", "message": "Invalid file type. Please upload an image file (jpg, jpeg, png)."}), 400
 
    try:
        response = requests.post(url, files={'file': file}, headers={})
        response.raise_for_status()
        print("Response status:", response.status_code)
        print("Response body:", response.json())  # Assuming response is JSON
 
        return jsonify({"status": "success", "data": response.json()}), 200
    except requests.exceptions.RequestException as e:
        print("Request failed:", e)
        return jsonify({"status": "failure", "message": "Error executing query", "error": str(e)}), 500

@app.route('/')
def default():
    return jsonify("hello world")

if __name__ == '__main__':
      app.run(debug=True,host="localhost",port=4000)