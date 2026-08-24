from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Float, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

DATABASE_URL = "sqlite:///./insurance_crm.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Database Models ---
class ManagerDB(Base):
    __tablename__ = "managers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    hours = Column(Float)
    targets = Column(Float)
    status = Column(String, default="Active")

class DispositionDB(Base):
    __tablename__ = "dispositions"
    id = Column(Integer, primary_key=True, index=True)
    booker_name = Column(String)
    lead_name = Column(String)
    disposition = Column(String)
    notes = Column(String, nullable=True)

Base.metadata.create_all(bind=engine)

# --- Pydantic Schemas ---
class ManagerCreate(BaseModel):
    name: str
    hours: float
    targets: float
    status: str = "Active"

class ManagerResponse(ManagerCreate):
    id: int
    class Config:
        orm_mode = True

class DispositionCreate(BaseModel):
    booker_name: str
    lead_name: str
    disposition: str
    notes: str = None

class DispositionResponse(DispositionCreate):
    id: int
    class Config:
        orm_mode = True

app = FastAPI(title="Insurance Department CRM & Operations System", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def seed_data():
    db = SessionLocal()
    if db.query(ManagerDB).count() == 0:
        initial_managers = [
            ("Aaron Robertson", 20.0, 20.0), ("Andrew Gallagher", 30.0, 30.0),
            ("Anthony Retone", 150.0, 150.0), ("Antonio Mullins", 20.0, 20.0),
            ("Ariel McAlister", 20.0, 20.0), ("Arturo Romero", 40.0, 40.0),
            ("Bo Freeman", 90.0, 90.0), ("Bonnie Verhulst", 40.0, 40.0),
            ("Brandon Bennett", 40.0, 40.0), ("Bryan Stoddard", 30.0, 30.0),
            ("Carlos O'Briant", 40.0, 40.0), ("Connor Hogan", 40.0, 40.0),
            ("Connor O'Donnell (MO)", 48.0, 48.0), ("Dalton Lance", 40.0, 40.0),
            ("Daniel Shepherd", 40.0, 40.0), ("Danielle Johnson", 20.0, 20.0),
            ("Demarcus White", 20.0, 20.0), ("Destiny Okungbowa", 40.0, 40.0),
            ("Devin Anderson", 20.0, 20.0), ("Dexter Radcliffe", 40.0, 40.0),
            ("Eddie Bierals", 40.0, 40.0), ("Galen Houser", 40.0, 40.0),
            ("Gerard Hatoum", 40.0, 40.0), ("Grace Roberts", 20.0, 20.0),
            ("Hunter Levi", 60.0, 60.0), ("Jacob Carmell", 20.0, 20.0),
            ("Jaden Ross", 20.0, 20.0), ("James Mathews", 40.0, 40.0),
            ("James Sherwood", 20.0, 20.0), ("Jesse Spencer", 40.0, 40.0),
            ("Jihad \"Jared\" OTTALLAH", 30.0, 30.0), ("Kahlil Blakely", 20.0, 20.0),
            ("Katie Powderly", 20.0, 20.0), ("Kevin Clark", 30.0, 30.0),
            ("Kyle Lewicki (CA)", 40.0, 40.0), ("Leatha Jones", 30.0, 30.0),
            ("Lisa Richardson", 20.0, 20.0), ("Macie Nelson", 40.0, 40.0),
            ("Marcus Celano", 30.0, 30.0), ("Michael Chachel", 40.0, 40.0),
            ("Michael Johnson", 20.0, 20.0), ("Michael North", 40.0, 40.0),
            ("Michele Faul (NJ)", 40.0, 40.0), ("Mitchell Mickovic", 30.0, 30.0),
            ("Monica Lee", 40.0, 40.0), ("Nicholas Boker", 20.0, 20.0),
            ("Nick Chuma", 60.0, 60.0), ("Omar Billy", 40.0, 40.0),
            ("Orit Danino", 30.0, 30.0), ("Rodrigo Gomez", 22.0, 22.0),
            ("Rubin Chaimov", 30.0, 30.0), ("Saleem Mustafa", 90.0, 90.0),
            ("Sam Main", 20.0, 20.0), ("Tami Chaimov", 30.0, 30.0),
            ("Thomas Joe-Kamara", 30.0, 30.0), ("Torin Cassani", 40.0, 40.0),
            ("Tristin Miser", 40.0, 40.0), ("Vickram Gurjar", 40.0, 40.0),
            ("Zach Lavelley", 20.0, 20.0), ("Zachary Wrightsil", 20.0, 20.0)
        ]
        for name, hrs, tgt in initial_managers:
            db.add(ManagerDB(name=name, hours=hrs, targets=tgt, status="Active"))
        db.commit()
    db.close()

@app.get("/api/managers", response_model=list[ManagerResponse])
def get_managers(db: Session = Depends(get_db)):
    return db.query(ManagerDB).all()

@app.post("/api/managers", response_model=ManagerResponse)
def upsert_manager(manager: ManagerCreate, db: Session = Depends(get_db)):
    db_mgr = db.query(ManagerDB).filter(ManagerDB.name == manager.name).first()
    if db_mgr:
        db_mgr.hours = manager.hours
        db_mgr.targets = manager.targets
        db_mgr.status = manager.status
    else:
        db_mgr = ManagerDB(name=manager.name, hours=manager.hours, targets=manager.targets, status=manager.status)
        db.add(db_mgr)
    db.commit()
    db.refresh(db_mgr)
    return db_mgr

@app.get("/api/metrics")
def get_metrics():
    return {
        "total_bookers_hours": 2376,
        "billable_hours": 1940,
        "additional_hours": 90,
        "weekly_target_hours": 308,
        "active_week": "08-23-26 TO 08-28-26"
    }

@app.get("/api/links")
def get_operational_links():
    return [
        {"title": "Additional Appointments", "url": "#"},
        {"title": "Bookers' Weekly Schedule", "url": "#"},
        {"title": "Additional Hours", "url": "#"},
        {"title": "Beastmode Attendance/Reliability", "url": "#"},
        {"title": "Working Hour Dispute Template", "url": "#"},
        {"title": "Script", "url": "#"},
        {"title": "Zoom Outbound Caller ID", "url": "#"},
        {"title": "EOD Gform", "url": "#"},
        {"title": "Pre-shift Report", "url": "#"},
        {"title": "1st Shift Report", "url": "#"},
        {"title": "2nd Shift Report", "url": "#"},
        {"title": "EOD Report", "url": "#"}
    ]

@app.get("/api/dispositions", response_model=list[DispositionResponse])
def get_dispositions(db: Session = Depends(get_db)):
    return db.query(DispositionDB).all()

@app.post("/api/dispositions", response_model=DispositionResponse)
def create_disposition(disp: DispositionCreate, db: Session = Depends(get_db)):
    db_disp = DispositionDB(**disp.dict())
    db.add(db_disp)
    db.commit()
    db.refresh(db_disp)
    return db_disp
