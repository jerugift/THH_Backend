from flask import Flask, request, jsonify
import mysql.connector
import pandas as pd

#app = Flask(__name__)

def get_user_role_and_jobs(email,table):
    try:
        # Connect to the MySQL database
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root123',
            database='antony'
        )
        cursor = conn.cursor()

        # Check if the email exists in the user_info table
        cursor.execute("SELECT Role FROM user_info WHERE email = %s", (email,))
        user_info = cursor.fetchone()

        if not user_info:
            return jsonify({"status":"Failure","message": "Email not found in the user_info table."}), 401

        role = user_info[0]
        print(f"Role: {role}")

        if role == 'admin':
            # If the user is an admin, retrieve all job details
            if table == "candidate_info":       
                cursor.execute("SELECT email, GROUP_CONCAT(DISTINCT job_id ORDER BY job_id DESC SEPARATOR '\n') AS job_ids FROM job_detail GROUP BY email")         
                job_details = cursor.fetchall()
                #cursor.execute(f"SELECT distinct(email),job_id FROM job_detail;")    
            elif table == "validation":
                cursor.execute("SELECT email, GROUP_CONCAT(DISTINCT job_id ORDER BY job_id DESC SEPARATOR '\n') AS job_ids FROM validation GROUP BY email")
                job_details = cursor.fetchall()
                #cursor.execute(f"SELECT distinct(email),job_id FROM validation;")    
            elif table == "link_extractor":
                cursor.execute("SELECT email, GROUP_CONCAT(DISTINCT job_id ORDER BY job_id DESC SEPARATOR '\n') AS job_ids FROM link_extractor GROUP BY email")
                job_details = cursor.fetchall()
                #cursor.execute(f"SELECT distinct(email),job_id,jd FROM link_extractor;") - jd has not been included in the above query

        else:
            # If the user is not an admin, retrieve job details for the given email
            if table == "candidate_info":
                cursor.execute("SELECT email, GROUP_CONCAT(DISTINCT job_id ORDER BY job_id DESC SEPARATOR '\n') AS job_ids FROM job_detail WHERE email = %s", (email,))
                job_details = cursor.fetchall()
                #cursor.execute("SELECT job_id FROM job_detail WHERE email = %s", (email,))
            elif table == "validation":
                cursor.execute("SELECT email, GROUP_CONCAT(DISTINCT job_id ORDER BY job_id DESC SEPARATOR '\n') AS job_ids FROM validation WHERE email = %s", (email,))
                job_details = cursor.fetchall()
                #cursor.execute("SELECT job_id FROM validation WHERE email = %s", (email,)) 
            elif table == "link_extractor":
                cursor.execute("SELECT email, GROUP_CONCAT(DISTINCT job_id ORDER BY job_id DESC SEPARATOR '\n') AS job_ids FROM link_extractor WHERE email = %s", (email,))
                job_details = cursor.fetchall()
                #cursor.execute("SELECT job_id,jd FROM link_extractor WHERE email = %s", (email,)) - jd has not been included in the above query        
            

        # job_details = cursor.fetchall()
        print(job_details)

        if  job_details[0][0] is None and job_details[0][1] is None:
            return jsonify({"status":"Failure","message": "No job details found for the given email. Go and fetch to show database."}),401

        # Get the column names
        columns = [desc[0] for desc in cursor.description]

        # Convert the job details to a DataFrame
        job_details_df = pd.DataFrame(job_details, columns=columns)
        job_details_json = job_details_df.to_json(orient='records')

        return jsonify({"status": "Success", "message": "Job details retrieved successfully.", "data": job_details_json}), 200

    except mysql.connector.Error as err:
        return jsonify({"status": "Failure", "message": f"Error: {err}"}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


# @app.route('/get-job-details', methods=['GET'])
# def get_job_details():
#     email = request.args.get('email')
#     if not email:
#         return jsonify({"message": "Email parameter is missing", "data": []})
    
#     return get_user_role_and_jobs(email)

# if __name__ == '__main__':
#     app.run(debug=True)



# endpoint - http://127.0.0.1:5000/get-job-details?email=vasan@devpozent.com





