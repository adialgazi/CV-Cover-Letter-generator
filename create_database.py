import sqlite3
from sqlite3 import Error
import base64
import uuid
import json

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded_string

def decode_base64_to_image(encoded_string, output_path):
    with open(output_path, "wb") as image_file:
        image_file.write(base64.b64decode(encoded_string))

def create_connection(db_file="database.db"):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"Connected to SQLite database version {sqlite3.version}")
    except Error as e:
        print(e)
    return conn

def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def main():
    database = "database.db"
    # Existing tables creation SQL
    sql_create_applicants_table = """CREATE TABLE IF NOT EXISTS applicants (
                                        uuid TEXT PRIMARY KEY UNIQUE,
                                        contact_info JSON,
                                        professional_summary TEXT,
                                        photo_base64 TEXT
                                    );"""

    sql_create_education_table = """CREATE TABLE IF NOT EXISTS education (
                                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        applicant_uuid TEXT,
                                        school_name TEXT,
                                        level TEXT,
                                        start_date TEXT,
                                        end_date TEXT,
                                        gpa REAL,
                                        field_of_study TEXT,
                                        achievements TEXT, 
                                        extra_notes TEXT,
                                        FOREIGN KEY (applicant_uuid) REFERENCES applicants (uuid)
                                    );"""

    sql_create_projects_table = """CREATE TABLE IF NOT EXISTS projects (
                                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        applicant_uuid TEXT,
                                        project_name TEXT,
                                        project_description TEXT,
                                        links TEXT, 
                                        extra_notes TEXT,
                                        FOREIGN KEY (applicant_uuid) REFERENCES applicants (uuid)
                                    );"""

    sql_create_work_experience_table = """CREATE TABLE IF NOT EXISTS work_experience (
                                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                                            applicant_uuid TEXT,
                                            title TEXT,
                                            company_name TEXT,
                                            achievements LIST,  
                                            extra_notes TEXT,
                                            FOREIGN KEY (applicant_uuid) REFERENCES applicants (uuid)
                                        );"""

    sql_create_volunteer_work_table = """CREATE TABLE IF NOT EXISTS volunteer_work (
                                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                                            applicant_uuid TEXT,
                                            organization TEXT,
                                            role TEXT,
                                            details TEXT, 
                                            FOREIGN KEY (applicant_uuid) REFERENCES applicants (uuid)
                                        );"""

    sql_create_languages_table = """CREATE TABLE IF NOT EXISTS languages (
                                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        applicant_uuid TEXT,
                                        language TEXT,
                                        proficiency_level TEXT,
                                        extra_notes TEXT,
                                        FOREIGN KEY (applicant_uuid) REFERENCES applicants (uuid)
                                    );"""

    sql_create_certifications_table = """CREATE TABLE IF NOT EXISTS certifications (
                                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                                            applicant_uuid TEXT,
                                            certification_name TEXT,
                                            issuing_organization TEXT,
                                            issue_date TEXT,
                                            expiry_date TEXT,
                                            credential_id TEXT,
                                            credential_url TEXT,
                                            FOREIGN KEY (applicant_uuid) REFERENCES applicants (uuid)
                                        );"""

    sql_create_awards_table = """CREATE TABLE IF NOT EXISTS awards (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    applicant_uuid TEXT,
                                    award_name TEXT,
                                    awarding_organization TEXT,
                                    date_received TEXT,
                                    description TEXT,
                                    FOREIGN KEY (applicant_uuid) REFERENCES applicants (uuid)
                                );"""

    sql_create_skills_table = """CREATE TABLE IF NOT EXISTS skills (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    applicant_uuid TEXT,
                                    skill_name TEXT,
                                    proficiency_level TEXT,
                                    category TEXT,
                                    FOREIGN KEY (applicant_uuid) REFERENCES applicants (uuid)
                                );"""

    sql_create_personal_projects_table = """CREATE TABLE IF NOT EXISTS personal_projects (
                                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                applicant_uuid TEXT,
                                                project_name TEXT,
                                                project_description TEXT,
                                                links TEXT,
                                                extra_notes TEXT,
                                                FOREIGN KEY (applicant_uuid) REFERENCES applicants (uuid)
                                            );"""



    conn = create_connection(database)
    if conn is not None:
        # Create existing tables
        create_table(conn, sql_create_applicants_table)
        create_table(conn, sql_create_education_table)
        create_table(conn, sql_create_projects_table)
        create_table(conn, sql_create_work_experience_table)
        create_table(conn, sql_create_volunteer_work_table)
        create_table(conn, sql_create_languages_table)
        create_table(conn, sql_create_certifications_table)
        create_table(conn, sql_create_awards_table)
        create_table(conn, sql_create_skills_table)
        create_table(conn, sql_create_personal_projects_table)
        print("Tables created successfully")
    else:
        print("Error! Cannot create the database connection.")

if __name__ == "__main__":
    conn = create_connection("database.db")
    sql = """ALTER TABLE applicants RENAME COLUMN uuid to applicant_uuid;"""
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
