from agents import set_default_openai_key, set_trace_processors
from braintrust import init_logger
from config import settings
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from libs.db import get_session
from sqlalchemy import text
from config import settings
from braintrust.wrappers.openai import BraintrustTracingProcessor
from routers import agent_router, history_router
import truststore

truststore.inject_into_ssl()
init_logger(project="Neteng", api_key=settings.BRAINTRUST_API_KEY)
set_trace_processors([BraintrustTracingProcessor(init_logger("Neteng", api_key=settings.BRAINTRUST_API_KEY))])
set_default_openai_key(settings.OPENAI_API_KEY)

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
  
## For UI
app.mount(
    "/",
    StaticFiles(directory="frontend/build/client", html=True),
)