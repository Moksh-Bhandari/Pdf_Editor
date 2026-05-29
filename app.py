from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

import os
import shutil
import uuid
import json
import time

# ======================================================
# change 4.1
# IMAGE OPTIMIZATION IMPORTS
# ======================================================
from PIL import Image

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
# change 3.1
# FILE SIZE LIMITS
# ======================================================
MAX_PDF_SIZE = 20 * 1024 * 1024      # 20 MB
MAX_IMAGE_SIZE = 10 * 1024 * 1024    # 10 MB

# ======================================================
# change 4.1
# IMAGE OPTIMIZATION ENGINE
# ======================================================
def optimize_image(input_path, output_path):
    """
    Compress and optimize images before PDF generation.
    """

    try:

        img = Image.open(input_path)

        # Convert transparent images safely
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        # Resize huge images
        MAX_WIDTH = 1600
        MAX_HEIGHT = 1600

        img.thumbnail((MAX_WIDTH, MAX_HEIGHT))

        # Save optimized JPEG
        img.save(
            output_path,
            format="JPEG",
            quality=70,
            optimize=True
        )

        return output_path

    except Exception as e:

        print("Image Optimization Error:", e)

        return input_path

# ======================================================
# STATIC FILES
# ======================================================
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# ======================================================
# change 3.4.2
# AUTO DELETE AFTER 1 MINUTE WITH RETRY
# ======================================================
def delete_after_delay(files_list):
    """
    Wait 60 seconds then safely delete files.
    """

    time.sleep(60)

    for file_path in files_list:

        for attempt in range(5):

            try:

                if os.path.exists(file_path):

                    os.remove(file_path)

                    print("Deleted:", file_path)

                    break

            except Exception as e:

                print(f"Retry {attempt + 1} failed:", e)

                time.sleep(2)

        else:

            print("Could not delete:", file_path)

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

        # ======================================================
        # Parse JSON Data
        # ======================================================
        data = json.loads(student_data)

        # ======================================================
        # Unique Job ID
        # ======================================================
        job_id = str(uuid.uuid4())

        # ======================================================
        # Validate PDF
        # ======================================================
        if not pdf_file.filename.lower().endswith(".pdf"):

            raise HTTPException(
                status_code=400,
                detail="Only PDF template file allowed."
            )

        pdf_file.file.seek(0, 2)
        pdf_size = pdf_file.file.tell()
        pdf_file.file.seek(0)

        if pdf_size > MAX_PDF_SIZE:

            raise HTTPException(
                status_code=400,
                detail="PDF exceeds 20 MB limit."
            )

        # ======================================================
        # Save Uploaded PDF
        # ======================================================
        pdf_name = f"{job_id}_{pdf_file.filename}"

        pdf_path = os.path.join(
            UPLOAD_DIR,
            pdf_name
        )

        with open(pdf_path, "wb") as buffer:

            shutil.copyfileobj(pdf_file.file, buffer)

        pdf_file.file.close()

        # ======================================================
        # change 4.1
        # SAVE + OPTIMIZE IMAGES
        # ======================================================
        image_paths = []

        for img in images:

            if img.filename:

                # ======================================================
                # Validate image size
                # ======================================================
                img.file.seek(0, 2)
                image_size = img.file.tell()
                img.file.seek(0)

                if image_size > MAX_IMAGE_SIZE:

                    raise HTTPException(
                        status_code=400,
                        detail=f"Image '{img.filename}' exceeds 10 MB limit."
                    )

                # ======================================================
                # Save original image
                # ======================================================
                img_name = f"{job_id}_{img.filename}"

                img_path = os.path.join(
                    UPLOAD_DIR,
                    img_name
                )

                with open(img_path, "wb") as buffer:

                    shutil.copyfileobj(img.file, buffer)

                img.file.close()

                # ======================================================
                # Optimized image path
                # ======================================================
                optimized_img_path = os.path.join(
                    UPLOAD_DIR,
                    f"optimized_{job_id}_{img.filename}.jpg"
                )

                # Compress image
                optimize_image(
                    img_path,
                    optimized_img_path
                )

                # Use optimized image
                image_paths.append(optimized_img_path)

        print("Total Images Received:", len(image_paths))

        # ======================================================
        # Output Path
        # ======================================================
        exp_no = data.get("exp_no", "X")

        output_filename = f"APSIT_Report_Exp{exp_no}.pdf"

        output_path = os.path.join(
            OUTPUT_DIR,
            f"{job_id}_{output_filename}"
        )

        # ======================================================
        # Generate Final PDF
        # ======================================================
        finalize_portfolio_report(
            pdf_path,
            output_path,
            data,
            image_paths
        )

        # ======================================================
        # change 4.1
        # DELETE ORIGINAL + OPTIMIZED FILES
        # ======================================================
        files_to_delete = [pdf_path, output_path]

        for img in images:

            if img.filename:

                original_path = os.path.join(
                    UPLOAD_DIR,
                    f"{job_id}_{img.filename}"
                )

                optimized_path = os.path.join(
                    UPLOAD_DIR,
                    f"optimized_{job_id}_{img.filename}.jpg"
                )

                files_to_delete.append(original_path)
                files_to_delete.append(optimized_path)

        # ======================================================
        # change 2.1
        # AUTO DELETE TASK
        # ======================================================
        background_tasks.add_task(
            delete_after_delay,
            files_to_delete
        )

        # ======================================================
        # Return PDF
        # ======================================================
        return FileResponse(
            path=output_path,
            media_type="application/pdf",
            filename=output_filename
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

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