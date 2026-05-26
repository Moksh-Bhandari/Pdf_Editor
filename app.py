from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

import os
import shutil
import uuid
import json
import time

from core.master_engine import finalize_portfolio_report

# ======================================================
# APP CONFIG
# ======================================================
app = FastAPI(
    title="APSIT PDF Editor",
    version="1.0.0"
)

# ======================================================
# BASE PATHS
# ======================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

# Create folders if missing
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ======================================================
# STATIC FILES
# ======================================================
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# ======================================================
# change 2.1
# AUTO DELETE AFTER 1 MINUTE
# ======================================================
def delete_after_delay(files_list):
    """
    Wait 60 seconds then delete files.
    """
    time.sleep(60)

    for file_path in files_list:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print("Deleted:", file_path)

        except Exception as e:
            print("Delete Error:", e)


# ======================================================
# HOME PAGE
# ======================================================
@app.get("/", response_class=HTMLResponse)
async def home():
    try:
        index_path = os.path.join(TEMPLATES_DIR, "index.html")

        with open(index_path, "r", encoding="utf-8") as file:
            return file.read()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ======================================================
# GENERATE REPORT
# ======================================================
@app.post("/generate-report")
async def generate_report(
    background_tasks: BackgroundTasks,
    student_data: str = Form(...),
    pdf_file: UploadFile = File(...),
    images: list[UploadFile] = File(default=[])
):
    try:
        # ----------------------------------------------
        # Parse JSON Data
        # ----------------------------------------------
        data = json.loads(student_data)

        # ----------------------------------------------
        # Unique Job ID
        # ----------------------------------------------
        job_id = str(uuid.uuid4())

        # ----------------------------------------------
        # Save Uploaded PDF
        # ----------------------------------------------
        if not pdf_file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=400,
                detail="Only PDF template file allowed."
            )

        pdf_name = f"{job_id}_{pdf_file.filename}"
        pdf_path = os.path.join(UPLOAD_DIR, pdf_name)

        with open(pdf_path, "wb") as buffer:
            shutil.copyfileobj(pdf_file.file, buffer)

        # ==================================================
        # change 2.2
        # Close uploaded pdf handle after saving
        # ==================================================
        pdf_file.file.close()

        # ----------------------------------------------
        # Save Images
        # ----------------------------------------------
        image_paths = []

        for img in images:
            if img.filename:

                img_name = f"{job_id}_{img.filename}"
                img_path = os.path.join(UPLOAD_DIR, img_name)

                with open(img_path, "wb") as buffer:
                    shutil.copyfileobj(img.file, buffer)

                # ==========================================
                # change 2.2
                # Close uploaded image handle after saving
                # ==========================================
                img.file.close()

                image_paths.append(img_path)

        print("Total Images Received:", len(image_paths))

        # ----------------------------------------------
        # Output Path
        # ----------------------------------------------
        exp_no = data.get("exp_no", "X")

        output_filename = f"APSIT_Report_Exp{exp_no}.pdf"

        output_path = os.path.join(
            OUTPUT_DIR,
            f"{job_id}_{output_filename}"
        )

        # ----------------------------------------------
        # Generate PDF
        # ----------------------------------------------
        finalize_portfolio_report(
            pdf_path,
            output_path,
            data,
            image_paths
        )

        # ==================================================
        # change 2.1
        # Schedule delete after 60 sec
        # ==================================================
        files_to_delete = [pdf_path, output_path] + image_paths

        background_tasks.add_task(
            delete_after_delay,
            files_to_delete
        )

        # ----------------------------------------------
        # Return File
        # ----------------------------------------------
        return FileResponse(
            path=output_path,
            media_type="application/pdf",
            filename=output_filename
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ======================================================
# RUN SERVER DIRECTLY
# ======================================================
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )