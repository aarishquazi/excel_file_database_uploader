from fastapi import FastAPI, UploadFile, File, Request, Form, Depends, status
from fastapi.responses import JSONResponse, HTMLResponse, StreamingResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import pandas as pd
import pymssql
import io
from typing import List
import os
import logging
from fastapi import HTTPException

# Import your DB credentials
from credential import server, database, username, password

from fastapi.responses import RedirectResponse


app = FastAPI()

# Session middleware for user authentication
app.add_middleware(SessionMiddleware, secret_key='AE3HMRH5mR2PO7ZnA2r4pF3NdcnFSh2CyFZdG1ug0b8')

# Static and template setup
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Configs
ALLOWED_EXTENSIONS = {".xlsx"}
MAX_TOTAL_FILE_SIZE = 200 * 1024 * 1024  # 200MB
COLUMNS_REQUIRED = [
    "Bill Date", "Bill ID", "HID", "Hospital Description", "SubSepcialization Description",
    "Service Description", "Department", "Unit Head", "Patient Category", "Patient Name",
    "Age", "Gender", "Hospital Expenses", "Login Name", "District", "State", "Patient Mobile No"
]

logging.basicConfig(level=logging.INFO)

@app.exception_handler(401)
async def unauthorized_exception_handler(request: Request, exc: HTTPException):
    return RedirectResponse("/login")

# Database connection
def get_db_connection():
    return pymssql.connect(server=server, user=username, password=password, database=database)

# Dependency to get current user from session
def get_current_user(request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user

# Login Page
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Login Submit
@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    conn = get_db_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        request.session["user"] = user["username"]
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})

# Logout
@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=status.HTTP_302_FOUND)

# Upload Page (protected)
@app.get("/", response_class=HTMLResponse)
async def get_upload_page(request: Request, user: str = Depends(get_current_user)):
    return templates.TemplateResponse("upload.html", {"request": request, "username": user})

# Preview Files (protected)
@app.post("/preview-files/")
async def preview_files(
    request: Request,
    files: List[UploadFile] = File(...),
    rowsToPreview: int = Form(...),
    user: str = Depends(get_current_user)
):
    total_size = sum(file.size for file in files)
    if total_size > MAX_TOTAL_FILE_SIZE:
        return JSONResponse(status_code=400, content={"error": "Total file size exceeds 200MB."})

    preview_data = []
    for file in files:
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            return JSONResponse(status_code=400, content={"error": f"{file.filename} is not a valid Excel file (.xlsx)."})

        try:
            file_bytes = await file.read()
            df = pd.read_excel(io.BytesIO(file_bytes), dtype=str)

            missing = [col for col in COLUMNS_REQUIRED if col not in df.columns]
            if missing:
                return JSONResponse(status_code=400, content={"error": f"{file.filename} missing: {', '.join(missing)}"})

            preview_data.append({
                "file": file.filename,
                "records": df[COLUMNS_REQUIRED].fillna("").head(rowsToPreview).to_dict(orient="records")
            })

        except Exception as e:
            return JSONResponse(status_code=500, content={"error": f"Error reading {file.filename}: {str(e)}"})

    return {"status": "preview", "files": preview_data}

@app.post("/upload-confirmed-stream/")
async def upload_confirmed_stream(
    request: Request,
    files: List[UploadFile] = File(...),
    user: str = Depends(get_current_user)
):
    file_data_list = []
    for file in files:
        file_bytes = await file.read()
        file_data_list.append((file.filename, file_bytes))

    def stream_response():
        total_rows = 0
        inserted = skipped = 0
        merged_df = pd.DataFrame()

        # Merge all files into one DataFrame
        for filename, file_bytes in file_data_list:
            try:
                df = pd.read_excel(io.BytesIO(file_bytes), dtype=str)
                df = df[COLUMNS_REQUIRED].copy()

                df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
                df = df.where(pd.notnull(df), None)
                df.dropna(subset=["Bill ID", "Service Description"], inplace=True)
                df.drop_duplicates(subset=["Bill ID", "Service Description"], inplace=True)
                df.sort_values(by="Bill Date", inplace=True)

                merged_df = pd.concat([merged_df, df], ignore_index=True)
                total_rows += len(df)

            except Exception as e:
                yield f"data: {{\"error\": \"Failed to process {filename}: {str(e)}\"}}\n\n"
                continue

        conn = get_db_connection()
        cursor = conn.cursor()

        insert_query = """
            INSERT INTO IHMS (
                Bill_Date, Bill_ID, HID, Hospital_Description,
                SubSepcialization_Description, Service_Description, Department, Unit_Head,
                Patient_Category, Patient_Name, Age, Gender, Hospital_Expenses,
                Login_Name, District, State, Patient_Mobile_No
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        for idx, (_, row) in enumerate(merged_df.iterrows()):
            try:
                cursor.execute(insert_query, (
                    row["Bill Date"], row["Bill ID"], row["HID"], row["Hospital Description"],
                    row["SubSepcialization Description"], row["Service Description"], row["Department"],
                    row["Unit Head"], row["Patient Category"], row["Patient Name"], row["Age"],
                    row["Gender"], row["Hospital Expenses"], row["Login Name"], row["District"],
                    row["State"], row["Patient Mobile No"]
                ))
                inserted += 1
            except pymssql.IntegrityError:
                skipped += 1

            percent = int((idx + 1) / total_rows * 100)
            yield f"data: {{\"progress\": {percent}}}\n\n"

        conn.commit()
        conn.close()

        yield f"data: {{\"done\": true, \"inserted\": {inserted}, \"skipped\": {skipped}}}\n\n"

    return StreamingResponse(stream_response(), media_type="text/event-stream")
