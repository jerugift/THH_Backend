# import mysql.connector as sql
# from flask import Flask, request, jsonify

# def connect_to_database():
#     try:
#         connection = sql.connect(
#             host="localhost",
#             user="root",
#             password="root123",
#             database="antony",
#             auth_plugin='mysql_native_password'
#         )
#         return connection
#     except sql.Error as error:
#         print("Error connecting to MySQL:", error)
#         return None
    
# def download_links(filters):
#     filters = request.json.get('filters', {})
#     #user_type = filters.get('user_type', 'user')
#     job_id = filters.get('job_id')
#     email = filters.get('email')
#     start_date = filters.get('start_date')
#     end_date = filters.get('end_date')

#     date_filter = ""
#     params = []

#     if start_date:
#         start_date+=" 00:00:00"
#         date_filter += f"AND ({{timestamp_field}} >= %s) "
#         params.append(start_date)
#         print(start_date)

#     if end_date:
#         end_date+=" 23:59:59"
#         date_filter += f"AND ({{timestamp_field}} <= %s) "
#         params.append(end_date)
#         print(end_date)
     
#     query = f"""
#         SELECT *
#         FROM link_extractor 
#         WHERE 
#             (Job_Id = %s OR %s IS NULL OR %s = '') 
#             AND (Email = %s OR %s IS NULL OR %s = '')
#             {date_filter}
#     """

#     params = [job_id, job_id, job_id, email, email, email] + params
#     query = query.format(timestamp_field="Event_Timestamp")
#     print(query)




import mysql.connector as sql
#from flask import Flask, request, jsonify, send_file, make_response
import pandas as pd

# app = Flask(__name__)

def connect_to_database():
    try:
        connection = sql.connect(
            host="localhost",
            user="root",
            password="root123",
            database="antony",
            auth_plugin='mysql_native_password'
        )
        return connection
    except sql.Error as error:
        print("Error connecting to MySQL:", error)
        return None


# if __name__ == '__main__':
#     app.run(debug=True)
