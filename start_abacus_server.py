import uvicorn
from abacus_server.analysis_pipeline_service.start_pipeline import start_pipeline

if __name__ == "__main__":

    start_pipeline()
    uvicorn.run("abacus_server.abacus_api.main:app", host="127.0.0.1", port=5000,
                log_level="info", reload=True)
