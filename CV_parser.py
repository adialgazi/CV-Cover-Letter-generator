import requests
import json
from pypdf import PdfReader
from openai import OpenAI
import update_database
import ast
import re
import logging
import os


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger(__name__)


url = 'http://localhost:8080'
FORMAT = {
    "applicant_data": "{\"full_name\": \"[Full Name]\", \"email\": \"[Email Address]\", \"phone\": \"[Phone Number]\", \"professional_summary\": \"[Brief Professional Summary]\", \"title\": \"[Current Title or Position]\"}",
    "education": "[{\"school_name\": \"[Institution Name]\", \"level\": \"[Degree Level]\", \"start_date\": \"[Start Date]\", \"end_date\": \"[End Date]\", \"gpa\": [GPA], \"field_of_study\": \"[Field of Study]\", \"achievements\": \"[Key Achievements]\", \"extra_notes\": \"[Additional Notes]\"}]",
    "projects": "[{\"project_name\": \"[Project Name]\", \"project_description\": \"[Project Description]\", \"extra_notes\": \"[Technologies Used and Other Notes]\"}]",
    "work_experience": "[{\"title\": \"[Job Title]\", \"company_name\": \"[Company Name]\", \"achievements\": \"[Key Achievements in the Role]\", \"extra_notes\": \"[Additional Notes]\"}]",
    "skills": "[{\"name\": \"[Skill Name]\", \"level\": \"[Skill Level]\"}]",
    "languages": "[{\"name\": \"[Language]\", \"level\": \"[Proficiency Level]\"}]",
    "volunteering": "[{\"organization\": \"[Organization Name]\", \"role\": \"[Role]\", \"details\": \"[Details of the Volunteer Work]\"}]"
}

def extract_text_from_cv(cv):
    reader = PdfReader(cv)
    page = reader.pages[0]
    text = page.extract_text()
    return text

def output_format(text):
    client = None
    try:
        api_key = os.environ.get('API_KEY')
        client = OpenAI(api_key=api_key)
    except Exception as e:
        logger(f'Error while connecting to OpenAI: {str(e)}')
    prompt = (f"""You are a professional recruiter, perfect for helping candidates get their dream jobs.
                     Given the following text parsed from an applicant's CV, rewrite it in a format suitable for
                     adding it to our database. It is very important that you won't add data that is not real
                     about the candidate.
                     This is the applicant's data: {text}
                     Output only the python dictionary, without any explanation or details, do it according to this format: {FORMAT}
                     Notice that besides "applicant_data", all items in the json are lists because they can have multiple values.
                     Make sure to avoid using ' in the text, as it'll break the json parsing.""")
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="gpt-3.5-turbo"
    )
    applicant_data = chat_completion.choices[0].message.content
    # logger("applicant_data:")
    # logger(applicant_data)

    applicant_data = re.sub(r'([a-zA-Z0-9])\'([a-zA-Z0-9])', r'\1\2', applicant_data)
    applicant_data = ast.literal_eval(applicant_data)

    for key in applicant_data:
        if not isinstance(applicant_data[key], str) or (applicant_data[key][0] not in ['{', '[']):
            applicant_data[key] = json.dumps(applicant_data[key])
    return applicant_data


def insert_data_to_database(applicant_data, education, projects, work_experience,
                            skills, languages, volunteering):
    conn = update_database.create_connection("database.db")

    education = json.loads(education)
    projects = json.loads(projects)
    work_experience = json.loads(work_experience)
    skills = json.loads(skills)
    languages = json.loads(languages)
    volunteering = json.loads(volunteering)

    applicant_uuid = update_database.insert_applicant(conn, applicant_data)

    for edu in education:
        update_database.insert_education(conn, (applicant_uuid,) + tuple(edu.values()))

    for work in work_experience:
        update_database.insert_work_experience(conn, (applicant_uuid,) + tuple(work.values()))

    for project in projects:
        update_database.insert_project(conn, (applicant_uuid,) + tuple(project.values()))

    for skill in skills:
        update_database.insert_skills(conn, (applicant_uuid,) + tuple(skill.values()))

    for language in languages:
        update_database.insert_language(conn, (applicant_uuid,) + tuple(language.values()))

    for vol in volunteering:
        update_database.insert_volunteering(conn, (applicant_uuid,) + tuple(vol.values()))

    return {"success": True, "message": "Data submitted successfully", "applicant_uuid": str(applicant_uuid)}


def api_call(applicant_data):
    response = insert_data_to_database(**applicant_data)
    if response["success"]:
        print("Submission successful.")
    else:
        print(f"Submission failed with message: {response['message']}")
    return response

def main(cv):
    text = extract_text_from_cv(cv)
    applicant_data = output_format(text)
    result = api_call(applicant_data)
    return result

if __name__ == "__main__":
    pass
    main('static/CV/Sharon Shechter CV.pdf')
    # main('C:/Users/ilai.avron/Downloads/Ilai_Av_Ron_CV_2_pdfrest_compressed-pdf.pdf')