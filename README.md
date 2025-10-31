
# 🏠 HostelManager – Flask Web Application

## Overview
**HostelManager** is a hostel management system built using **Flask (Python)** and **Microsoft SQL Server (MSSQL)**.  
It helps administrators manage students, rooms, allocations, payments, and maintenance activities efficiently.  
The project was developed during my **SIWES (Student Industrial Work Experience Scheme)** training at **Microware Solution Limited**, Ogudu, Lagos.

---

##  Features
-  **Student Management** – Add, view, edit, and delete student records.  
-  **Room Management** – Create and monitor hostel rooms and capacity.  
-  **Allocation System** – Assign students to available rooms.  
-  **Payment Tracking** – Record and verify student payments.  
-  **Maintenance Reporting** – Log and update maintenance issues.  
-  **Dashboard** – View hostel statistics and reports in real-time.  

> **Note:** Students must complete **payment** before they can be allocated to a room.

---

##  Tech Stack
| Component | Technology |
|------------|-------------|
| **Backend** | Flask (Python) |
| **Frontend** | HTML, CSS, JavaScript |
| **Database** | Microsoft SQL Server (MSSQL) |
| **ORM/Connection** | PyODBC |
| **Environment Config** | python-dotenv |
| **IDE Used** | Visual Studio Code (VS Code) |

---

##  Installation and Setup

### **System Requirements**
- Python 3.10 or later  
- Microsoft SQL Server 2019 or later  
- SQL Server Management Studio (SSMS)  
- Visual Studio Code  
- Git (optional)

---

### **Installation Steps**

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/HostelManager.git
   cd HostelManager
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the database**
   - Open SQL Server Management Studio (SSMS).  
   - Create a database named **HostelManager**.  
   - Run the SQL scripts provided in `/database/` to create all tables.

5. **Create a `.env` file**
   ```
   DB_SERVER=localhost
   DB_NAME=HostelManager
   DB_USER=your_username
   DB_PASSWORD=your_password
   ```

6. **Run the application**
   ```bash
   python app.py
   ```
   Visit `http://127.0.0.1:5000` in your browser.

---

##  Usage Guide
- Log in as an admin.  
- Register students and record their payments.  
- Allocate rooms only to students who have completed payments.  
- Update or view maintenance requests and overall statistics via the dashboard.

---

##  Folder Structure
```
HostelManager/
│
├── __pycache__
      |app
├── static/
│   ├── style.css
│   └──allocation.js
|   └──dashboard.js
|   └──login.js
|   └──maintenance.js
|   └──payments.js
|   └──rooms.js
|   └──script.js
|   └──students.js
├── templates/
│   ├── index.html
│   ├── students.html
│   ├── rooms.html
│   ├── allocations.html
│   ├── payments.html
│   └── maintenance.html
|   └──login.html
├── templates/
│   ├── Include
│   ├── Lib\site-packages/
│   ├── Scripts/
│   ├── gitignore
│   └── pyvenv.cfg
|   └──README.md
|   
│
│
├── .env
├── requirements.txt
└── README.md
```

---

## Future Enhancements
- Add user authentication for students.  
- Integrate online payment gateways.  
- Implement analytics dashboard.  
- Deploy the system to a live server.

---

##  Author
**Mercy Ottah-Nelson**  
Department of Computer Science,  
Lagos State University  
**Supervisor:** Prof. Aribisala Benjamin  
