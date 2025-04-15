# 📄 Excel File Upload Portal for IHMS System

A secure and user-friendly **FastAPI-based portal** for uploading and previewing Excel files, with session-based login, dark mode, and real-time upload tracking. Designed to streamline data collection for hospital billing and diagnostic services.

![badge](https://img.shields.io/badge/Built_with-FastAPI-0ba360?style=for-the-badge&logo=fastapi&logoColor=white)

## 🚀 Features

✅ Secure login with session cookies  
✅ Upload **multiple Excel files** (.xlsx only)  
✅ **Live progress** with streaming updates (SSE)  
✅ **Preview rows** before upload  
✅ **Duplicate detection** (`Bill ID + Service Description`)  
✅ Modern **UI with Dark Mode** and Logout  
✅ Clean file validation with download template

## 📁 Project Structure

```
📦 ihms_excel_uploader/
├── main.py                 # Main FastAPI application
├── credential.py           # 🔒 Your DB credentials (excluded from Git)
├── templates/
│   ├── login.html
│   └── upload.html
├── static/
│   └── sample_template.xlsx
├── .gitignore
├── requirements.txt
└── README.md
```

## ⚙️ Tech Stack

- 🚀 [FastAPI](https://fastapi.tiangolo.com)
- 🎨 [Bootstrap 5](https://getbootstrap.com/)
- 📊 [Pandas](https://pandas.pydata.org/)
- 🛡️ [SessionMiddleware](https://www.starlette.io/middleware/)
- 🧠 [pymssql](https://pymssql.readthedocs.io/)

## 🧪 Getting Started

### 🔹 1. Clone the repository

```bash
git clone https://github.com/your-username/excel_file_database_uploader.git
cd excel_file_database_uploader
```

### 🔹 2. Create and activate a virtual environment

```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### 🔹 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 🔑 Step 4: Create `credential.py`

Since this file is excluded from Git (for security), create a file called `credential.py` in your project root with this content:

```python
server = "your_sql_server"
database = "your_database"
username = "your_username"
password = "your_password"
```

## ▶️ Step 5: Run the Server

```bash
uvicorn main:app --reload
```

Visit: [http://localhost:8000](http://localhost:8000)

## 📦 Sample Upload Template

Use the provided template file for clean uploads:  
👉 [static/sample_template.xlsx](static/sample_template.xlsx)

## 📊 Default SQL Table Schema

### 🔹 IHMS Data Table

```sql
CREATE TABLE IHMS (
    Bill_Date DATE,
    Bill_ID VARCHAR(100),
    HID VARCHAR(50),
    Hospital_Description VARCHAR(255),
    SubSepcialization_Description VARCHAR(255),
    Service_Description VARCHAR(255),
    Department VARCHAR(100),
    Unit_Head VARCHAR(100),
    Patient_Category VARCHAR(50),
    Patient_Name VARCHAR(100),
    Age VARCHAR(20),
    Gender VARCHAR(20),
    Hospital_Expenses VARCHAR(50),
    Login_Name VARCHAR(100),
    District VARCHAR(100),
    State VARCHAR(100),
    Patient_Mobile_No VARCHAR(20)
);
```

### 🔐 User Login Table

```sql
CREATE TABLE users (
    id INT PRIMARY KEY IDENTITY(1,1),
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL
);
```

## 🌙 Screenshots

| Upload Page | Dark Mode |
|-------------|-----------|
| ![light](https://via.placeholder.com/400x250?text=Upload+Preview) | ![dark](https://via.placeholder.com/400x250?text=Dark+Mode) |

## 🔮 Roadmap

- [x] Multiple Excel file uploads with merging  
- [x] Live progress bar  
- [x] Duplicate row skipping  
- [x] Secure login/logout  
- [ ] Password hashing  
- [ ] Upload audit logs per user  
- [ ] Admin dashboard with reports  

## 🧠 Credits

Built by **Installer Guru**  
📍 Jaipur, Rajasthan  
📧 Email: [you@example.com]