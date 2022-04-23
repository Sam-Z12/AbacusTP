import os
import zipfile
from os import path
from io import BytesIO
from typing import List
from fastapi import APIRouter, UploadFile, File, Depends
from fastapi.responses import FileResponse, StreamingResponse

from .. import oauth2

parent_dir: str = path.dirname(__file__)
abacus_api_path = path.dirname(parent_dir)
abacus_server_path = path.dirname(abacus_api_path)
data_source_temp_path = f"{abacus_server_path}/analysis_pipeline_service/data_sources/source_template.py"
data_analysis_temp_path = f"{abacus_server_path}/analysis_pipeline_service/data_analyses/analysis_template.py"
data_decision_temp_path = f"{abacus_server_path}/analysis_pipeline_service/data_decisions/decision_template.py"
temp_path = f"{abacus_server_path}/analysis_pipeline_service/pipeline_templates"

router = APIRouter(
    prefix="/pipeline",
    tags=['Pipeline'])


def copy_save_file(file, contents):
    filename: str = file.filename
    if filename.endswith("source.py"):
        parent_folder = "data_sources"
    elif filename.endswith("analysis.py"):
        parent_folder = "data_analyses"
    elif filename.endswith("decision.py"):
        parent_folder = "data_decisions"
    else:
        parent_folder = "trash"

    new_file = f"{abacus_server_path}/analysis_pipeline_service/{parent_folder}/{filename}"
    with open(new_file, 'wb') as f:
        f.write(contents)


def zipfiles(file_list):
    io = BytesIO()
    zip_sub_dir = "pipeline_templates"
    zip_filename = f"{zip_sub_dir}.zip"
    with zipfile.ZipFile(io, mode='w', compression=zipfile.ZIP_DEFLATED) as zip:
        for fpath in file_list:
            zip.write(fpath)
        # close zip
        zip.close()
    return StreamingResponse(
        iter([io.getvalue()]),
        media_type="python files/x-zip-compressed",
        headers={"Content-Disposition": f"attachment;filename={zip_filename}"}
    )


def zipdir(dir_path):
    io = BytesIO()
    parentDir = path.dirname(dir_path)
    with zipfile.ZipFile(io, 'w') as myzip:
        for root, directories, files in os.walk(dir_path):
            # always take whats after the parentDir for the filename going in the zip
            zipFileName = root[len(parentDir):]
            print(zipFileName)
            for file in files:
                myzip.write(os.path.join(root, file), os.path.join(
                    zipFileName, file), compress_type=zipfile.ZIP_DEFLATED)

    return StreamingResponse(
        iter([io.getvalue()]),
        media_type="python files/x-zip-compressed",
        headers={"Content-Disposition": f"attachment;filename=pipeline_templates.zip"}
    )


@router.get("/")
def pipeline_overview(current_user: int = Depends(oauth2.get_current_user)):
    return {"Message": "Welcome to the analysis pipeline home"}


@router.post("/upload")
async def upload(files: List[UploadFile] = File(...), current_user: int = Depends(oauth2.get_current_user)):
    for file in files:
        contents = await file.read()
        copy_save_file(file, contents)

    return {"Uploaded Filenames": [file.filename for file in files]}


@router.get("/template", )
def get_template(current_user: int = Depends(oauth2.get_current_user)):
    return_files = [data_source_temp_path, data_analysis_temp_path]

    return zipdir(temp_path)
