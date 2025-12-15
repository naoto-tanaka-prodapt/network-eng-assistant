import os

from braintrust import init_logger
from config import settings
from typing import Annotated
from fastapi import FastAPI, Form, HTTPException, Request, Response
# from routers import job_application_router, job_board_router, llm_router, job_post_router
# from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from libs.db import get_session
from sqlalchemy import text
from config import settings
from routers import agent_router, history_router
# from auth import authenticate_admin, AdminAuthzMiddleware, AdminSessionMiddleware, delete_admin_session
# from schemas import AdminLoginForm

init_logger(project="Prodapt", api_key=settings.BRAINTRUST_API_KEY)

app = FastAPI()

app.include_router(agent_router.router)
app.include_router(history_router.router)



@app.get("/api/health")
async def health():
  try:
      with get_session() as session:
        session.execute(text("SELECT 1"))
      return {"status": "OK! Hello World"}
  except Exception as e:
      print(f"Failed to connect: {e}")
      return {"status": "ng"}
  
# ## local file directory
# if not settings.PRODUCTION:
#   app.mount("/uploads", StaticFiles(directory="uploads"))

# ## Auth
# @app.post("/api/admin-login")
# async def admin_login(response: Response, admin_login_form: Annotated[AdminLoginForm, Form()]):
#    auth_response = authenticate_admin(admin_login_form.username, admin_login_form.password)
#    if auth_response is not None:
#       secure = settings.PRODUCTION
#       response.set_cookie(key="admin_session", value=auth_response, httponly=True, secure=secure, samesite="Lax")
#       return {}
#    else:
#       raise HTTPException(status_code="403")
   
# @app.get("/api/me")
# async def me(req: Request):
#   return {"is_admin": req.state.is_admin}

# @app.post("/api/admin-logout")
# async def admin_logout(request: Request, response: Response):
#   delete_admin_session(request.cookies.get("admin_session"))
#   secure = settings.PRODUCTION
#   response.delete_cookie(key="admin_session", httponly=True, secure=secure, samesite="LaX")
  
## For UI
app.mount(
    "/",
    StaticFiles(directory="frontend/build/client", html=True),
)