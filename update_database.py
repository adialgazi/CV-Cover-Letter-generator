import sqlite3
from sqlite3 import Error
import json
import uuid
import create_database

def create_connection(db_file="database.db"):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"Connected to SQLite database version {sqlite3.version}")
    except Error as e:
        print(e)
    return conn



def insert_applicant(conn, applicant_json):
    applicant_uuid = uuid.uuid4()
    applicant = json.loads(applicant_json)

    sql = ''' INSERT INTO applicants(applicant_uuid, full_name, email, phone_number, professional_summary, title, photo_base64)
                  VALUES(?,?,?,?,?,?,?) '''

    applicant_data = (
        str(applicant_uuid),
        applicant.get('full_name', ''),
        applicant.get('email', ''),
        applicant.get('phone', ''),
        applicant.get('professional_summary', ''),
        applicant.get('title', ''),
        None
    )
    cur = conn.cursor()
    cur.execute(sql, applicant_data)
    conn.commit()
    return str(applicant_uuid)

def insert_education(conn, education):
    sql = ''' INSERT INTO education(applicant_uuid,school_name,level,start_date,end_date,gpa,field_of_study,achievements,extra_notes)
              VALUES(?,?,?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    print(education)
    cur.execute(sql, education)
    conn.commit()
    return cur.lastrowid

def insert_project(conn, project):
    sql = ''' INSERT INTO projects(applicant_uuid,project_name,project_description,extra_notes)
              VALUES(?,?,?,?) '''
    cur = conn.cursor()
    print(project)
    cur.execute(sql, project)
    conn.commit()
    return cur.lastrowid

def insert_work_experience(conn, work_experience):
    sql = ''' INSERT INTO work_experience(applicant_uuid,title,company_name,achievements,extra_notes)
              VALUES(?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, work_experience)
    conn.commit()
    return cur.lastrowid

def insert_skills(conn, skill):
    sql = ''' INSERT INTO skills(applicant_uuid,skill_name,proficiency_level)
            VALUES(?,?,?)'''
    cur = conn.cursor()
    cur.execute(sql, skill)
    conn.commit()
    return cur.lastrowid

def insert_language(conn, language):
    sql = ''' INSERT INTO languages(applicant_uuid,language,proficiency_level)
                VALUES(?,?,?)'''
    cur = conn.cursor()
    cur.execute(sql, language)
    conn.commit()
    return cur.lastrowid

def insert_volunteering(conn, volunteering):
    sql = ''' INSERT INTO volunteer_work(applicant_uuid,organization,role,details)
            VALUES(?,?,?,?)'''
    cur = conn.cursor()
    cur.execute(sql, volunteering)
    conn.commit()
    return cur.lastrowid

def get_applicant(conn, uuid):
    cur = conn.cursor()
    cur.execute("SELECT * FROM applicants WHERE applicant_uuid=?", (uuid,))
    return cur.fetchone()


def get_all_applicant_data(conn, applicant_uuid):
    data = {}
    cur = conn.cursor()
    cur.execute("SELECT * FROM applicants WHERE applicant_uuid=?", (applicant_uuid,))
    applicant_data = cur.fetchone()
    if not applicant_data:
        return None
    data['applicant'] = {
        'uuid': applicant_data[0],
        'email': applicant_data[1],
        'phone_number': applicant_data[2],
        'professional_summary': applicant_data[3],
        'full_name': applicant_data[4],
        'photo_base64': applicant_data[5],
    }

    cur.execute(
        "SELECT school_name, level, field_of_study, gpa, start_date, end_date FROM education WHERE applicant_uuid=?",
        (applicant_uuid,))
    education_data = []
    for row in cur.fetchall():
        modified_row = (
            row[0],  # school_name
            row[1],  # level
            row[2],  # field_of_study
            f"gpa: {row[3]}" if row[3] else "",  # Add prefix to gpa if not empty
            f"start date: {row[4]}" if row[4] else "",  # Add prefix to start_date if not empty
            f"end date: {row[5]}" if row[5] else "",  # Add prefix to end_date if not empty
        )
        education_data.append(modified_row)
    data['education'] = education_data
    cur.execute("SELECT * FROM projects WHERE applicant_uuid=?", (applicant_uuid,))
    data['projects'] = cur.fetchall()
    cur.execute("SELECT title, company_name, achievements FROM work_experience WHERE applicant_uuid=?", (applicant_uuid,))
    data['work_experience'] = cur.fetchall()
    cur.execute("SELECT skill_name, proficiency_level FROM skills WHERE applicant_uuid=?", (applicant_uuid,))
    data['skills'] = cur.fetchall()
    cur.execute("SELECT language, proficiency_level FROM languages WHERE applicant_uuid=?", (applicant_uuid,))
    data['languages'] = cur.fetchall()
    cur.execute("SELECT organization, role, details  FROM volunteer_work WHERE applicant_uuid=?", (applicant_uuid,))
    data['volunteering'] = cur.fetchall()

    return data

