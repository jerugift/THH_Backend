
def create_tables_if_not_exist(cursor):
    # Create user_info table if not exists
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_info (
        ID INT NOT NULL AUTO_INCREMENT,
        username VARCHAR(255) DEFAULT NULL,
        password VARCHAR(255) DEFAULT NULL,
        email VARCHAR(255) NOT NULL,
        Role VARCHAR(255) DEFAULT NULL,
        PRIMARY KEY (ID)
    )
    """)

    # Create job_detail table if not exists
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS job_detail (
        id INT NOT NULL AUTO_INCREMENT,
        Job_ID VARCHAR(255) NOT NULL,
        email VARCHAR(255) DEFAULT NULL,
        Event_timestamp TIMESTAMP NULL DEFAULT NULL,
        JD VARCHAR(4000) DEFAULT NULL,
        Skillset VARCHAR(255) DEFAULT NULL,
        PRIMARY KEY (id)
    )
    """)

    # Create candidate_info table if not exists
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS candidate_info (
        ID INT NOT NULL AUTO_INCREMENT,
        JOB_ID VARCHAR(255) DEFAULT NULL,
        Resume LONGTEXT,
        Signature VARCHAR(255) DEFAULT NULL,
        Name TEXT,
        Email VARCHAR(255) DEFAULT NULL,
        Mobile VARCHAR(10) DEFAULT NULL,
        Similarity FLOAT DEFAULT NULL,
        Relevant_experience LONGTEXT,
        PRIMARY KEY (ID)
    )
    """)

    # Create link_extractor table if not exists
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS link_extractor (
        id INT NOT NULL AUTO_INCREMENT,
        job_id INT DEFAULT NULL,
        jd TEXT,
        Booleanquery TEXT,
        email VARCHAR(255) DEFAULT NULL,
        name VARCHAR(255) DEFAULT NULL,
        link VARCHAR(512) DEFAULT NULL,
        Event_Timestamp TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (id)
    )
    """)
