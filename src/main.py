from fastapi import FastAPI
from fastapi.responses import FileResponse

from src.api.templates import router as template_router
from src.api.users import router as user_router

app = FastAPI()

app.include_router(template_router)
app.include_router(user_router)


@app.get("/")
async def read_index():
    return FileResponse("static/index.html")
