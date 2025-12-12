import random
import string
from io import BytesIO
from pypdf import PdfReader
from llm.evaluate_resume import evaluate_resume_with_ai
from models import JobApplicationAIEvaluation
from db import get_session

## Utils
def create_random_file_name(extention):
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=15))
    print(random_string)
    return random_string + extention

def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    reader = PdfReader(BytesIO(pdf_bytes))
    pages = []
    for p in reader.pages:
        text = p.extract_text() or ""
        pages.append(text)
    return "\n\n".join(pages).strip()

def evaluate_resume(resume_content, job_post_description, job_application_id):
   resume_raw_text = extract_text_from_pdf_bytes(resume_content)
   ai_evaluation = evaluate_resume_with_ai(resume_raw_text, job_post_description)
   with get_session() as session:
      evaluation = JobApplicationAIEvaluation(
         job_application_id = job_application_id,
         overall_score = ai_evaluation["overall_score"],
         evaluation = ai_evaluation
      )
      session.add(evaluation)
      session.commit()