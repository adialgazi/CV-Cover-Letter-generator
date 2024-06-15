from fastapi import FastAPI, Form, File, UploadFile, Request, Response, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sqlite3
from sqlite3 import Error
import json
import update_database, create_database
from pydantic import BaseModel
import os
import cover_letter
import logging
import base64
import multipart
from typing import List
import jinja2
from fastapi.middleware.cors import CORSMiddleware
from CV_generator import create_CV
from CV_parser import main as parse_CV
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger(__name__)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # REMEMBER TO FIX
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


DATABASE = 'database.db'

@app.post("/log")
async def log_message(request: Request):
    log_data = await request.json()
    message = log_data.get("message", "")
    level = log_data.get("level", "info").lower()

    logger = logging.getLogger("uvicorn")

    if level == "debug":
        logger.debug(message)
    elif level == "info":
        logger.info(message)
    elif level == "warning":
        logger.warning(message)
    elif level == "error":
        logger.error(message)
    else:
        raise HTTPException(status_code=400, detail="Invalid log level")

    return {"message": "Log received", "level": level, "log_message": message}

def get_db_connection():
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
    except Error as e:
        logger.error(e)
    return conn

@app.get("/", response_class=HTMLResponse)
async def index():
    with open("templates/index.html", "r") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@app.get("/login", response_class=HTMLResponse)
async def get_login():
    with open("templates/login.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@app.get("/signup", response_class=HTMLResponse)
async def get_signup():
    with open("templates/signup.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@app.get("/manual_signup", response_class=HTMLResponse)
async def get_manual_signup():
    with open("templates/manual_signup.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@app.post("/submit-cover-letter/{uuid}")
async def submit_cover_letter(uuid: str, coverLetterText: str = Form(...)):
    logger.info('Creating cover letter')
    directory = 'temporary_files'
    if not os.path.exists(directory):
        os.makedirs(directory)

    updated_file_path = cover_letter.main(coverLetterText, uuid)

    return FileResponse(
        path=updated_file_path,
        media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        filename=f"Cover_Letter_for_{uuid}.docx")

@app.post("/submit-cv/{uuid}")
async def submit_cv(uuid: str, coverLetterText: str = Form(...), templateSelect: str = Form(...)):
    logger.info('Selected template is: %s', templateSelect)
    directory = 'temporary_files'
    if not os.path.exists(directory):
        os.makedirs(directory)

    template_document_map = {
        'template1': 'static/templates/cv_template1.docx',
        'template2': 'static/templates/cv_template2.docx',
    }
    template_document = template_document_map.get(templateSelect, template_document_map['template1'])

    cv_path = create_CV(uuid, coverLetterText, template_document)

    return FileResponse(cv_path, media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                        filename=os.path.basename(cv_path))

@app.post("/automatic_signup")
async def automatic_signup(cv_file: UploadFile = File(...)):
    try:
        temp_dir = "temporary_files"
        os.makedirs(temp_dir, exist_ok=True)
        cv_file_path = os.path.join(temp_dir, cv_file.filename)
        with open(cv_file_path, "wb") as buffer:
            buffer.write(cv_file.file.read())
        result = parse_CV(cv_file_path)
        return JSONResponse(content={"message": "Signup successful!", "applicant_uuid": result["applicant_uuid"]})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during signup: {str(e)}")
@app.get("/generate-cover-letter/{uuid}", response_class=HTMLResponse)
async def generate_cover_letter(request: Request, uuid: str):
    return templates.TemplateResponse("generate_cover_letter.html", {"request": request, "uuid": uuid})

@app.get("/generate-cv/{uuid}", response_class=HTMLResponse)
async def generate_cv(request: Request, uuid: str):
    return templates.TemplateResponse("generate_cv.html", {"request": request, "uuid": uuid})

class SubmitFormSchema(BaseModel):
    applicant_data: str
    education: str
    projects: str
    work_experience: str
    skills: str
    languages: str
    volunteering: str

@app.post("/submit_form")
async def submit_form(body: SubmitFormSchema):
    logger.info('Manual creation with this data: \n %s', body)
    applicant_data = json.loads(body.applicant_data)
    education_data = json.loads(body.education)
    projects_data = json.loads(body.projects)
    work_experience_data = json.loads(body.work_experience)
    skills_data = json.loads(body.skills)
    languages_data = json.loads(body.languages)
    volunteering_data = json.loads(body.volunteering)

    # logger.info((applicant_data)

    conn = update_database.create_connection("database.db")

    applicant_uuid = update_database.insert_applicant(conn, json.dumps(applicant_data))

    for edu in education_data:
        update_database.insert_education(conn, (applicant_uuid,) + tuple(edu.values()))

    for work in work_experience_data:
        update_database.insert_work_experience(conn, (applicant_uuid,) + tuple(work.values()))

    for project in projects_data:
        update_database.insert_project(conn, (applicant_uuid,) + tuple(project.values()))

    for skill in skills_data:
        update_database.insert_skills(conn, (applicant_uuid,) + tuple(skill.values()))

    for language in languages_data:
        update_database.insert_language(conn, (applicant_uuid,) + tuple(language.values()))

    for vol in volunteering_data:
        update_database.insert_volunteering(conn, (applicant_uuid,) + tuple(vol.values()))

    return {"success": True, "message": "Data submitted successfully", "applicant_uuid": str(applicant_uuid)}

@app.post("/login")
async def post_login(uuid: str = Form(...)):
    return RedirectResponse(url=f"/dashboard/{uuid}", status_code=303)

@app.get("/dashboard/{uuid}", response_class=HTMLResponse)
async def dashboard(request: Request, uuid: str):
    logger.info('Accessing dashboard for %s', uuid)
    conn = get_db_connection()
    if conn:
        applicant = update_database.get_applicant(conn, uuid)
        if applicant:
            return templates.TemplateResponse("dashboard.html",
                                              {"request": request,
                                               "email": applicant[1],
                                               "phone_number": applicant[2],
                                               "full_name": applicant[4],
                                               "applicant": applicant})
        else:
            return RedirectResponse(url="/login?error=UUID not found", status_code=303)
    else:
        return RedirectResponse(url="/login?error=Database connection error", status_code=303)

@app.get("/get_applicant_data")
async def get_applicant_data(uuid: str):
    try:
        conn = update_database.create_connection()
        if conn is None:
            raise HTTPException(status_code=500, detail="Failed to connect to the database.")
        data = cover_letter.fetch_applicant_data(uuid, conn)
        if data is None:
            raise HTTPException(status_code=404, detail="Applicant data not found.")
        return data
    except Error as e:
        logging.error(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)