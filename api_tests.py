import requests
import json
import logging
import update_database
import os
from CV_generator import create_CV
from unittest.mock import patch
from CV_generator import create_user_profile

test_id = '6f6bb790-03a1-418a-80cf-1aaaa2e194b0'
url = 'http://localhost:8000/'
#url = 'https://cvimporver.azurewebsites.net/'

applicant_data = {
  "applicant_data": "{\"full_name\": \"Kavid Dalmanson\", \"email\": \"something@somewhere.com\", \"phone\": \"123-456-7890\", \"professional_summary\": \"Experienced software developer with a strong background in computer science and a passion for building scalable web applications.\", \"title\": \"Software Developer\"}",
  "education": "[{\"school_name\": \"Tech University\", \"level\": \"BSc\", \"start_date\": \"2014-09-01\", \"end_date\": \"2018-06-30\", \"gpa\": 3.8, \"field_of_study\": \"Computer Science\", \"achievements\": \"Graduated summa cum laude\", \"extra_notes\": \"Participated in a senior project that won the university's innovation award.\"}]",
  "projects": "[{\"project_name\": \"Project Alpha\", \"project_description\": \"A web application for real-time data analysis.\", \"extra_notes\": \"Used technologies include React, Node.js, and PostgreSQL.\"}]",
  "work_experience": "[{\"title\": \"Senior Software Developer\", \"company_name\": \"Innovatech Solutions\", \"achievements\": \"Led a team of developers in creating a multi-platform application.\", \"extra_notes\": \"Application increased company revenue by 20% within the first year.\"}]",
  "skills": "[{\"name\": \"JavaScript\", \"level\": \"Advanced\"}, {\"name\": \"Python\", \"level\": \"Intermediate\"}]",
  "languages": "[{\"name\": \"English\", \"level\": \"Fluent\"}, {\"name\": \"Spanish\", \"level\": \"Intermediate\"}]",
  "volunteering": "[{\"organization\": \"Code for Good\", \"role\": \"Volunteer Mentor\", \"details\": \"Mentored high school students in software development projects for non-profits.\"}]"
}

job_details = """
About the job
Who we are:



Firebolt is at the forefront of data analytics, offering cutting-edge cloud data warehouse solutions. Our innovative technology is designed to handle the most complex data challenges, providing unmatched speed and efficiency. Join us in our mission to revolutionize data analytics and help businesses unlock the full potential of their data.


About the Team:



Firebolt’s Metadata Team is responsible for components within the data warehouse that provide metadata information for firebolt control & dataplane. Aside from “user data”, Firebolt keeps meta-information to make user data accessible and useful. The challenge of the Metadata team is to hold this data and serve it with low latency in an ACID compliant way. We're solving challenges around high scalability, concurrency and performance, like implementing distributed transactions and snapshot isolation.


Roles and Responsibilities:



Take part in the definition of Firebolt’s product design and architecture
Design, build, and maintain Firebolt’s cutting-edge metadata solution
Work closely with other Firebolt teams to provide a seamless data experience


Requirements: 



3+ years as a backend engineer with at least 1.5 year using Go in production
Production experience with Kubernetes
Hands on experience in building and operating cloud native applications on AWS, GCP or Azure
Strong Linux fundamentals and an understanding of networking, including a variety of network protocols, especially AWS networking
Experience building and operating highly concurrent, highly available, and fault-tolerant distributed systems
Expertise in Algorithms, Data Structures, Concurrency and Design Patterns


A bonus if you have: 



Familiarity with databases such as FoundationDB, Aerospike or any high-performance KV-store
Familiarity with distributed computing, networking, lockless algorithms and data structures
Experience with message brokers and data/ stream processing (Kafka, RabbitMQ)
"""

def create_applicant(applicant_data):
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url+'/submit_form', headers=headers, data=json.dumps(applicant_data))
    if response.status_code == 200:
        print("Submission successful.")
        print(response.json())
    else:
        print(f"Submission failed with status code: {response.status_code}")
        print(response.text)

def generate_cl(uuid, description, save_path='downloaded_cover_letter.docx'):
    response = requests.post(f"{url}/submit-cover-letter/{uuid}", data={'coverLetterText': description})
    if response.status_code == 200:
        print("Cover letter submitted successfully.")
        with open(save_path, 'wb') as f:
            f.write(response.content)
        print(f"File saved as {save_path}")
    else:
        print(f"Failed to submit cover letter. Status code: {response.status_code}")
        print("Response text:", response.text)


def test_get_applicant_data(uuid):
    url = "http://localhost:8000/get_applicant_data"
    params = {'uuid': uuid}
    response = requests.get(url, params=params)

    if response.status_code == 200:
        print("Data fetched successfully.")
        print(response.json())
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        print("Response text:", response.text)


def test_create_CV():
    template_path = "static/templates/cv_template1.docx"
    expected_output_path = "static/templates/cv_template1_updated.docx"

    output_path = create_CV(test_id, job_details, template_path)
    print("output path: ")
    print(output_path)
    assert output_path == expected_output_path
    assert os.path.exists(expected_output_path)

    # Cleanup
    os.remove(expected_output_path)


@patch('CV_generator.get_all_applicant_data')
def test_create_user_profile(mock_get_data):
    mock_get_data.return_value = {
        "applicant": {
            "full_name": "Kavid Dalmanson",
            "email": "something@somewhere.com",
            "phone_number": "123-456-7890",
            "professional_summary": "Experienced software developer with a strong background in computer science and a passion for building scalable web applications.",
            "title": "Software Developer"
        },
        "education": [{
            "school_name": "Tech University",
            "level": "BSc",
            "start_date": "2014-09-01",
            "end_date": "2018-06-30",
            "gpa": 3.8,
            "field_of_study": "Computer Science",
            "achievements": "Graduated summa cum laude",
            "extra_notes": "Participated in a senior project that won the university's innovation award."
        }],
        "projects": [{
            "project_name": "Project Alpha",
            "project_description": "A web application for real-time data analysis.",
            "extra_notes": "Used technologies include React, Node.js, and PostgreSQL."
        }],
        "work_experience": [{
            "title": "Senior Software Developer",
            "company_name": "Innovatech Solutions",
            "achievements": "Led a team of developers in creating a multi-platform application.",
            "extra_notes": "Application increased company revenue by 20% within the first year."
        }],
        "skills": [{
            "name": "JavaScript",
            "level": "Advanced"
        }, {
            "name": "Python",
            "level": "Intermediate"
        }],
        "languages": [{
            "name": "English",
            "level": "Fluent"
        }, {
            "name": "Spanish",
            "level": "Intermediate"
        }],
        "volunteering": [{
            "organization": "Code for Good",
            "role": "Volunteer Mentor",
            "details": "Mentored high school students in software development projects for non-profits."
        }]
    }

    # Mock the OpenAI API response if necessary

    profile_dict = create_user_profile(test_id, job_details)
    print("profile dict: ")
    print(profile_dict)
    assert 'Full name' in profile_dict
    assert profile_dict['Full name'] == 'KAVID DALMANSON'
    assert 'email place holder' in profile_dict

# generate_cl('f7e7cdb1-c6e0-4f25-9963-56c08487bab8', job_details)
# create_applicant(applicant_data)
# print(update_database.get_all_applicant_data(update_database.create_connection(), '6b239e2b-1003-4fdf-aca1-a518abff6286'))
print(test_get_applicant_data(test_id))
test_create_CV()
test_create_user_profile()
