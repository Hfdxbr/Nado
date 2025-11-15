from datetime import datetime, timedelta, timezone

import jwt
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from src.api.templates import router as template_router
from src.api.users import router as user_router
from src.api import SessionDep
from src.database import PrivateUser
from src.utils import users as uu
from src.utils import templates as ut

app = FastAPI()
templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(template_router)
app.include_router(user_router)

SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=115)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user_from_request(request: Request, session: SessionDep):
    token = request.cookies.get("access_token")
    if token:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            return uu.get_by_email(email, session)
        except jwt.PyJWTError:
            return None
    return None


@app.get("/", response_class=HTMLResponse)
def home(request: Request, session: SessionDep):
    current_user = get_current_user_from_request(request, session)

    if not current_user:
        return RedirectResponse(url="/login", status_code=302)

    return RedirectResponse(url="/account", status_code=302)


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
def login(request: Request, session: SessionDep, email: str = Form(...), password: str = Form(...)):
    current_user = uu.get_by_email(email, session)
    if current_user is None:
        return RedirectResponse(url="/login", status_code=404)
    # if current_user.password_hash != uu.make_hash(PrivateUser(email=email, password=password)):
    #     return RedirectResponse(url="/login", status_code=401)
    token = create_access_token(data={"sub": email})
    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie("access_token", token, httponly=True)
    return response


@app.get("/logout")
def logout(request: Request):
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("access_token")
    return response


@app.get("/account", response_class=HTMLResponse)
def account(request: Request, session: SessionDep):
    current_user = get_current_user_from_request(request, session)

    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    tmpls = ut.get_user_templates(current_user.id, session)
    return templates.TemplateResponse("account.html", {"request": request, "user": current_user, "templates": tmpls})


@app.post("/account")
def account(request: Request, session: SessionDep, title: str = Form(...), repr: str = Form(...)):
    current_user = get_current_user_from_request(request, session)

    ut.create_template(ut.Template(title=title, repr=repr), session, user_id=current_user.id)
    return RedirectResponse(url="/", status_code=302)
