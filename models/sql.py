import mysql.connector
from datetime import datetime
import os
import base64

def job_detail(jd, key, email):
    #global new_jdid
    a = datetime.now()
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        database="antony",
        password="root123",
        port="3306",
        auth_plugin='mysql_native_password'
    )
    mycursor = mydb.cursor()

    mycursor.execute("SELECT MAX(id) FROM job_detail")
    result = mycursor.fetchone()

    max_id = result[0] if result[0] is not None else 0
    starts = 100
    new_jdid = f'Job id:{starts + max_id + 1}'
    p = open(jd, encoding='UTF-8').read() if os.path.exists(jd) else jd
    values_text = ""

    for key, value in key.items():
        if isinstance(value, list):
            values_text += f"{key}: {', '.join(value)}\n"
        else:
            values_text += f"{key}: {value}\n"

    sql = "INSERT INTO job_detail (Job_ID, email, Event_Timestamp, JD, Skillset) VALUES (%s, %s, %s, %s, %s)"
    val = [new_jdid, email, a, p, values_text]
    mycursor.execute(sql, val)
    mydb.commit()
    return new_jdid

def sql_data_push(df):
    connection = mysql.connector.connect(
        user="root",
        host="localhost",
        database="antony",
        password="root123",
        port="3306",
        auth_plugin='mysql_native_password'
    )
 
 
    cursor = connection.cursor()
    table_name = 'candidate_info'
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        ID INT AUTO_INCREMENT PRIMARY KEY,
        JOB_ID VARCHAR(255),
        RESUME TEXT,
        Signature Varchar(255),
        Name VARCHAR(255),
        Mobile VARCHAR(10),
        Email VARCHAR(255),
        Similarity FLOAT,
        Relevant_experience varchar(255)
    )
    """
    cursor.execute(create_table_query)
    cursor.execute(f"SELECT MAX(ID) FROM {table_name}")
    result = cursor.fetchone()
    if result[0] is not None:
        fixed_id = result[0] + 1              
       
    else:
        fixed_id = 1  
   
    for index, row in df.iterrows():
        insert_query = f"""
            INSERT INTO {table_name} (Job_ID, Resume, Signature, Name, Mobile, Email, Similarity )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (row['JOB_ID'], row['Resume'], row['Signature'], row['Name'], row['Mobile'], row['Email'], row['Similarity']))
   
    connection.commit()
    cursor.close()
    connection.close()
   
def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root123",
            database="antony",
            auth_plugin='mysql_native_password'
        )
        return connection
    except  mysql.connector.connect.Error as error:
        print("Error connecting to MySQL:", error)
        return None

import mysql.connector as sql
import pandas as pd
 
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

def generate_query(filters, table):
    user_type = filters.get('user_type', 'user')
    job_id = filters.get('job_id')
    email = filters.get('email')
    start_date = filters.get('start_date')
    end_date = filters.get('end_date')
    query=None

    if start_date and end_date and start_date > end_date:
        return None, "Error: Start date cannot be after the end date."

    if table == 'candidate_info' and job_id and email:
        connection = connect_to_database()
        if connection:
            cursor = connection.cursor()
            check_query = """
                SELECT COUNT(*)
                FROM job_detail
                WHERE Job_Id = %s AND Email = %s
            """
            cursor.execute(check_query, (job_id, email))
            match_count = cursor.fetchone()[0]
            connection.close()

            if match_count == 0:
                return None, "Error: Email and Job-ID do not match."
        else:
            return None, "Failed to connect to the database"

    elif table ==  "link_extractor" and job_id and email:
        connection = connect_to_database()
        if connection:
            cursor = connection.cursor()
            check_query = """
                SELECT COUNT(*)
                FROM link_extractor
                WHERE Job_Id = %s AND Email = %s
            """
            cursor.execute(check_query, (job_id, email))
            match_count = cursor.fetchone()[0]
            connection.close()

            if match_count == 0:
                return None, "Error: Email and Job-ID do not match."
        else:
            return None, "Failed to connect to the database"


    elif table == "validation" and job_id and email:
        connection = connect_to_database()
        if connection:
            cursor = connection.cursor()
            check_query = """
                SELECT COUNT(*)
                FROM validation
                WHERE Job_Id = %s AND Email = %s
            """
            cursor.execute(check_query, (job_id, email))
            match_count = cursor.fetchone()[0]
            connection.close()

            if match_count == 0:
                return None, "Error: Email and Job-ID do not match."
        else:
            return None, "Failed to connect to the database"

    date_filter = ""
    params = []

    if start_date:
        start_date+=" 00:00:00"
        date_filter += f"AND ({{timestamp_field}} >= %s) "
        params.append(start_date)
        print(start_date)

    if end_date:
        end_date+=" 23:59:59"
        date_filter += f"AND ({{timestamp_field}} <= %s) "
        params.append(end_date)
        print(end_date)

    if user_type == 'admin':
        if not job_id and not email and not start_date and not end_date:
            return None, "Choose a filter to search"

        elif table == "candidate_info":        
            query = f"""
                SELECT *
                FROM {table} t
                {"JOIN job_detail jd ON t.Job_Id = jd.Job_Id" if table == 'candidate_info' else ""}
                WHERE 
                    (t.Job_Id = %s OR %s IS NULL OR %s = '') 
                    AND (jd.Email = %s OR %s IS NULL OR %s = '') 
                    {date_filter}
                    ORDER BY Similarity DESC
            """
            params = [job_id, job_id, job_id, email, email, email] + params
            query = query.format(timestamp_field="jd.Event_Timestamp")
            print(query)

        elif table ==  "link_extractor":        
            query = f"""
                SELECT *
                FROM {table} 
                WHERE 
                    (Job_Id = %s OR %s IS NULL OR %s = '') 
                    AND (Email = %s OR %s IS NULL OR %s = '') 
                    {date_filter}
            """
            params = [job_id, job_id, job_id, email, email, email] + params
            query = query.format(timestamp_field="Event_Timestamp")
            print(query)

        elif table == "validation":        
            query = f"""
                SELECT *
                FROM {table}
                WHERE 
                    (Job_Id = %s OR %s IS NULL OR %s = '') 
                    AND (Email = %s OR %s IS NULL OR %s = '') 
                    {date_filter}
            """
            params = [job_id, job_id, job_id, email, email, email] + params
            query = query.format(timestamp_field="Event_Timestamp")
            print(query)            
        
    else:
        if not job_id and not start_date and not end_date:
            return None, "Choose a filter to search"

        elif not email:
            return None, "Error: Email is required for non-admin users."
            
        elif table == "candidate_info":        
            query = f"""
                SELECT *
                FROM {table} t
                {"JOIN job_detail jd ON t.Job_Id = jd.Job_Id" if table == 'candidate_info' else ""}
                WHERE 
                    (t.Job_Id = %s OR %s IS NULL OR %s = '') 
                    AND (jd.Email = %s)
                    {date_filter}
                ORDER BY t.Similarity DESC
            """
            params = [job_id, job_id, job_id, email] + params
            query = query.format(timestamp_field="jd.Event_Timestamp")
            print(query)

        elif table ==  "link_extractor":        
            query = f"""
                SELECT *
                FROM {table} 
                WHERE 
                    (Job_Id = %s OR %s IS NULL OR %s = '') 
                    AND (Email = %s)
                    {date_filter}
            """
            params = [job_id, job_id, job_id, email] + params
            query = query.format(timestamp_field="Event_Timestamp")
            print(query)

        elif table == "validation":        
            query = f"""
                SELECT *
                FROM {table} 
                WHERE 
                    (Job_Id = %s OR %s IS NULL OR %s = '') 
                    AND (Email = %s)
                    {date_filter}
            """
            params = [job_id, job_id, job_id, email] + params
            query = query.format(timestamp_field="Event_Timestamp")
            print(query)

    return query, params


def common_dash_func(filters, table):
    connection = connect_to_database()
    if connection:
        cursor = connection.cursor()
        query, params = generate_query(filters, table)

        if query is None:
            return {"status": "Failure", "message": params}, 400

        cursor.execute(query, params)
        data = cursor.fetchall()

        if not data:
            message = "No data found."
            if filters.get('start_date') and filters.get('end_date'):
                message = "No data found between the provided start and end dates."
            elif filters.get('start_date'):
                message = "No data found after the provided start date."
            elif filters.get('end_date'):
                message = "No data found before the provided end date."
            return {"status": "Failure", "message": message}, 404

        df = pd.DataFrame(data, columns=[desc[0] for desc in cursor.description])
        user_query=None

        if table == "validation":
            df['Document'] = df['Document'].apply(lambda x: base64.b64encode(x).decode('utf-8') if x else None)

        elif table == "link_extractor":
            user_query = f'Search results based on: {df["jd"][0]}' #.unique().tolist()
            print(user_query)

        connection.close()
        #print(df.to_dict(orient='records'))
        return {"status":"Success","data":df.to_dict(orient='records'), "query":user_query}, 200

    else:
        return {"status": "Failure", "message": "Failed to connect to the database"}, 500


def rel_rank(job_id, name, result):
    #global new_jdid
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        database="antony",
        password="root123",
        port="3306",
        auth_plugin='mysql_native_password'
    )
    mycursor = mydb.cursor()

    sql = f'''UPDATE candidate_info SET Relevant_experience = "{result}"
              WHERE JOB_ID = "{job_id}" AND 
              Name="{name}"'''
    #val = [result]
    mycursor.execute(sql)
    mydb.commit()
    return "Done"

