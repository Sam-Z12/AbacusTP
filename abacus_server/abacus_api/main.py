from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from . import db_models
from .database import abacus_api_engine
from .routers import coinbase, users, auth, paper_trade, analysis_pipeline
import uvicorn
db_models.Base.metadata.create_all(bind=abacus_api_engine)
""" 
run cmd uvicorn abacus_server.abacus_api.main:app --reload 
in the Abacus directory to start the api. Reload flag auto reloads api 
on file saves and is not needed in production.
"""
app = FastAPI()

origins = ["http://localhost",
           "http://localhost:3000"
           ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(coinbase.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(paper_trade.router)
app.include_router(analysis_pipeline.router)


@app.get("/")
async def root():
    return {"title": "Welcome to Abacus",
            "description": "Abacus is algorithmic trading platform aimed at making algorithm deployment easy!"}
