# code block for download_api_resumes with api(gpt)
from flask import Flask, request, jsonify, send_file, make_response
import mysql.connector
import json


# app = Flask(__name__)

def download_api_resumes(email_id, jd_id):
    try:
        # Connect to the MySQL database
        mydb = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root123',
            database='antony'
        )
        cursor = mydb.cursor()

        # Check if the email exists in the candidate_info table
        cursor.execute("SELECT * FROM candidate_info WHERE email = %s and job_id = %s", (email_id, jd_id))
        candidate_info = cursor.fetchall()        

        if not candidate_info:
            return jsonify({"message": "Email not found", "data": []}), 404
        
        cursor.execute("SELECT Name FROM candidate_info WHERE email = %s and job_id = %s", (email_id, jd_id))
        filename=cursor.fetchone()

        print(candidate_info[0][2])
        print("#########", filename[0])

        with open(f'Resume_{filename[0]}.txt',"w") as file:
            file.write(candidate_info[0][2])
        
        response = make_response(send_file(f'Resume_{filename[0]}.txt', as_attachment=True))
        response.headers['Success-Message'] = 'File downloaded successfully'

        return response, 200
        
    
    except mysql.connector.Error as err:
        return jsonify({"message": f"Error: {err}", "data": []}), 500
    finally:
        if mydb.is_connected():
            cursor.close()
            mydb.close()


# @app.route('/download_api_resumes', methods=['GET'])
# def download_api_resumes_route():
#     email_id = request.args.get('email')
#     jd_id= request.args.get('jd_id')
#     if not email_id:
#         return jsonify({"message": "Email ID is required", "data": []})
    
#     return download_api_resumes(email_id, jd_id)

# if __name__ == '__main__':
#     app.run(debug=True)
