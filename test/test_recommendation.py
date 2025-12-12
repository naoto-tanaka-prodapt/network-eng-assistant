import os
from models import JobBoard, JobPost, JobApplication
from vector_search import ingest_resume, ingest_resume_for_recommendataions, get_recommendation

def test_should_embed_text_and_add_to_vector_db(vector_store):
    ingest_resume("Siddharta\nSiddharta is an AI trainer", "siddharta.pdf", 1, vector_store)
    retriever = vector_store.as_retriever(search_kwargs={"k": 1})
    result = retriever.invoke("I am looking for an AI trainer")
    assert len(result) == 1
    assert "Siddharta" in result[0].page_content
    assert result[0].metadata['_id'] == 1


def test_background_task(vector_store):
    filename = "test/resumes/ProfileAndrewNg.pdf"
    with open(filename, "rb") as f:
        content = f.read()
    ingest_resume_for_recommendataions(content, filename, resume_id=1, vector_store=vector_store, job_post_id=10)
    retriever = vector_store.as_retriever(search_kwargs={"k": 1})
    result = retriever.invoke("I am looking for an AI trainer")
    assert "Andrew" in result[0].page_content


def test_retrieval_quality(vector_store):
    for id, filename in enumerate(os.listdir("test/resumes")):
        with open(f"test/resumes/{filename}", "rb") as f:
            content = f.read()
        ingest_resume_for_recommendataions(content, filename, id, vector_store)

    retriever = vector_store.as_retriever(search_kwargs={"k": 1})

    result = retriever.invoke("I am looking for an expert in AI")
    assert "Andrew" in result[0].page_content
    result = retriever.invoke("I am looking for an expert in Linux")
    assert "Linus" in result[0].page_content
    result = retriever.invoke("I am looking for an expert in Javascript")
    assert "Yuxi" in result[0].page_content
    result = retriever.invoke("I am looking for a generalist who can work in python and typescript")
    assert "Koudai" in result[0].page_content
    result = retriever.invoke("I am looking for a data journalist")
    assert "Simon" in result[0].page_content

def test_job_application_api(db_session, vector_store, client):
    job_board = JobBoard(slug="test", logo_path="http://example.com")
    db_session.add(job_board)
    db_session.commit()
    db_session.refresh(job_board)
    job_post = JobPost(title="AI Engineer", 
                       description="Need an AI Engineer", 
                       job_board_id = job_board.id)
    db_session.add(job_post)
    db_session.commit()
    db_session.refresh(job_post)
    filename = "test/resumes/ProfileAndrewNg.pdf"
    post_data = {
        "first_name": "Siddharta",
        "last_name": "Govindaraj",
        "email": "siddharta@gmail.com",
        "job_post_id": job_post.id
    }
    with open(filename, "rb") as f:
        response = client.post("/api/job-applications", data=post_data, files={"resume": ("ProfileAndrewNg.pdf", f, "application/pdf")})
    assert response.status_code == 200
    created_application = response.json()
    retriever = vector_store.as_retriever(search_kwargs={"k": 1})
    result = retriever.invoke("I am looking for an expert in AI")
    assert "Andrew" in result[0].page_content
    assert result[0].metadata["_id"] == created_application["id"]
    assert result[0].metadata["job_post_id"] == job_post.id

def test_get_recommendation(vector_store):
    # resume insert
    for id, filename in enumerate(os.listdir("test/resumes")):
        with open(f"test/resumes/{filename}", "rb") as f:
            content = f.read()
        ingest_resume_for_recommendataions(content, filename, id, vector_store)

    result = get_recommendation(
        description="We’re seeking a Forward Deployed Engineer. We want someone with 3+ years of software engineering experience with production systems. They should be rockstar programmers and problem solvers. They should have experience in a customer-facing technical role with a background in systems integration or professional services",
        vector_store=vector_store
    )
    assert "Koudai" in result.page_content
    
def test_api_job_post_recommandation(db_session, vector_store, client):
    job_board = JobBoard(slug="test", logo_path="http://example.com")
    db_session.add(job_board)
    db_session.commit()
    db_session.refresh(job_board)
    job_post = JobPost(title="AI Engineer", 
                       description="I am looking for a generalist who can work in python and typescript", 
                       job_board_id = job_board.id)
    another_job_post = JobPost(title="Duplicate role", 
                               description="I am looking for a generalist who can work in python and typescript", 
                               job_board_id = job_board.id)
    db_session.add(job_post)
    db_session.add(another_job_post)
    db_session.commit()
    db_session.refresh(job_post)
    db_session.refresh(another_job_post)
    test_resumes = [
        (another_job_post.id, 'Andrew', 'Ng', 'andrewng@gmail.com', 'ProfileAndrewNg.pdf'),
        (job_post.id, 'Koudai', 'Aono', 'koxudaxi@gmail.com', 'ProfileKoudaiAono.pdf')
    ]
    for target_post_id, first_name, last_name, email, filename in test_resumes:
        post_data = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "job_post_id": target_post_id
        }
        with open(f"test/resumes/{filename}", "rb") as f:
            response = client.post("/api/job-applications", data=post_data, files={"resume": (filename, f, "application/pdf")})
    response = client.get(f"/api/job-posts/{job_post.id}/recommend")
    assert response.status_code == 200
    data = response.json()
    assert data['first_name'] == 'Koudai'
    assert data['last_name'] == 'Aono'
