from fastapi import FastAPI
from app.database import engine, Base
from app.routers import papers, categories, reports

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Paper Search API")

app.include_router(papers.router, prefix="/papers", tags=["papers"])
app.include_router(categories.router, prefix="/categories", tags=["categories"])
app.include_router(reports.router, prefix="/reports", tags=["reports"])

@app.get("/")
def root():
    return {"message": "Paper Search API"}
