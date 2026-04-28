from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from pydantic import BaseModel
from typing import Optional

from app.database import Base, engine, SessionLocal
from app.models import User
from app.schemas import UserCreate, UserLogin
from app.security import hash_password, verify_password, create_access_token

app = FastAPI()
templates = Jinja2Templates(directory="templates")

Base.metadata.create_all(bind=engine)


# ---------------- DB ----------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------- Calculation Model ----------------
class Calculation(Base):
    __tablename__ = "calculations"

    id = Column(Integer, primary_key=True, index=True)
    operation = Column(String, nullable=False)
    num1 = Column(Float, nullable=False)
    num2 = Column(Float, nullable=False)
    result = Column(Float, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))


Base.metadata.create_all(bind=engine)


# ---------------- Schemas ----------------
class CalcCreate(BaseModel):
    operation: str
    num1: float
    num2: float


class CalcUpdate(BaseModel):
    operation: Optional[str] = None
    num1: Optional[float] = None
    num2: Optional[float] = None


# ---------------- Helper ----------------
def do_calc(op, a, b):
    if op == "add":
        return a + b
    if op == "subtract":
        return a - b
    if op == "multiply":
        return a * b
    if op == "divide":
        if b == 0:
            raise HTTPException(status_code=400, detail="Cannot divide by zero")
        return a / b
    raise HTTPException(status_code=400, detail="Invalid operation")


def get_current_user(db: Session = Depends(get_db)):
    user = db.query(User).first()

    if not user:
        raise HTTPException(status_code=401, detail="No user found")

    return user


# ---------------- Pages ----------------
@app.get("/")
def home():
    return {"message": "API running"}


@app.get("/register-page")
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/login-page")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


# ---------------- Auth ----------------
@app.post("/register")
def register(data: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == data.email).first()

    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    user = User(
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password)
    )

    db.add(user)
    db.commit()

    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}


@app.post("/login")
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}


# ---------------- BREAD ----------------

@app.get("/calculations")
def browse_calculations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Calculation).filter(
        Calculation.user_id == current_user.id
    ).all()


@app.get("/calculations/{calc_id}")
def read_calculation(
    calc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    calc = db.query(Calculation).filter(
        Calculation.id == calc_id,
        Calculation.user_id == current_user.id
    ).first()

    if not calc:
        raise HTTPException(status_code=404, detail="Not found")

    return calc


@app.post("/calculations")
def add_calculation(
    data: CalcCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = do_calc(data.operation, data.num1, data.num2)

    calc = Calculation(
        operation=data.operation,
        num1=data.num1,
        num2=data.num2,
        result=result,
        user_id=current_user.id
    )

    db.add(calc)
    db.commit()
    db.refresh(calc)
    return calc


@app.put("/calculations/{calc_id}")
def edit_calculation(
    calc_id: int,
    data: CalcUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    calc = db.query(Calculation).filter(
        Calculation.id == calc_id,
        Calculation.user_id == current_user.id
    ).first()

    if not calc:
        raise HTTPException(status_code=404, detail="Not found")

    if data.operation is not None:
        calc.operation = data.operation
    if data.num1 is not None:
        calc.num1 = data.num1
    if data.num2 is not None:
        calc.num2 = data.num2

    calc.result = do_calc(calc.operation, calc.num1, calc.num2)

    db.commit()
    db.refresh(calc)
    return calc


@app.delete("/calculations/{calc_id}")
def delete_calculation(
    calc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    calc = db.query(Calculation).filter(
        Calculation.id == calc_id,
        Calculation.user_id == current_user.id
    ).first()

    if not calc:
        raise HTTPException(status_code=404, detail="Not found")

    db.delete(calc)
    db.commit()

    return {"message": "Deleted successfully"}


import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)