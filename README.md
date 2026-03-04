# 🏠 HostelTrackerERP – Flask Web Application

## 📖 Overview
**HostelTrackerERP** is a hostel management system built using **Flask (Python)** and **PostgreSQL**.  
It helps administrators manage students, rooms, allocations, payments, and maintenance activities efficiently.  

The project was developed during my **SIWES (Student Industrial Work Experience Scheme)** training at **Microware Solution Limited**, Ogudu, Lagos.

---

## ✨ Features
* **Student Management** – Add, view, edit, and delete student records.
* **Room Management** – Create and monitor hostel rooms and capacity.
* **Allocation System** – Assign students to available rooms.
* **Payment Tracking** – Record and verify student payments with auto-generated receipt numbers.
* **Maintenance Reporting** – Log and update maintenance issues.
* **Dashboard** – View hostel statistics and reports in real-time.

> ⚠️ **Note:** Students must complete **payment** before they can be allocated to a room.

---

## 🛠️ Tech Stack
| Component | Technology |
| :--- | :--- |
| **Backend** | Flask (Python) |
| **Frontend** | HTML, CSS, Vanilla JavaScript |
| **Database** | PostgreSQL (Hosted on Render) |
| **Database Driver** | `psycopg2-binary` |
| **Environment Config**| `python-dotenv` |
| **IDE Used** | Visual Studio Code (VS Code) |

---

## 🚀 Installation and Local Setup

### System Requirements
* Python 3.10 or later
* Git

### Steps to Run Locally

**1. Clone the repository**
```bash
git clone [https://github.com/callmedevmercy/hosteltrackererp.git](https://github.com/callmedevmercy/hosteltrackererp.git)
cd hosteltrackererp
2. Create and activate a virtual environment

Bash
python -m venv venv
venv\Scripts\activate
3. Install dependencies

Bash
pip install -r requirements.txt
4. Set up the environment variables
Create a .env file in the root directory. You will need your cloud database URL to connect:

Plaintext
DATABASE_URL=your_postgresql_database_url
FLASK_SECRET_KEY=your_secret_key
5. Initialize the Database
Run the setup script to automatically build the tables in your PostgreSQL database and create the default admin account:

Bash
python setup_db.py
6. Run the application

Bash
python app.py
Visit http://127.0.0.1:5000 in your browser.

💻 Usage Guide
Log in as an admin (Default setup credentials — Username: admin, Password: admin123).

Register students and record their payments.

Allocate rooms only to students who have completed payments.

Update or view maintenance requests and overall statistics via the dashboard.

📂 Folder Structure
Plaintext
HostelManager/
├── static/
│   ├── style.css
│   ├── allocation.js
│   ├── dashboard.js
│   ├── login.js
│   ├── maintenance.js
│   ├── payments.js
│   ├── rooms.js
│   ├── script.js
│   └── students.js
├── templates/
│   ├── index.html
│   ├── students.html
│   ├── rooms.html
│   ├── allocations.html
│   ├── payments.html
│   ├── maintenance.html
│   └── login.html
├── venv/                  # Virtual Environment (Ignored in Git)
├── .env                   # Environment Variables (Ignored in Git)
├── .gitignore             # Git ignore rules
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── setup_db.py            # Database initialization script
└── README.md              # Project documentation
🔮 Future Enhancements
Add user authentication and personalized portals for students.

Integrate online payment gateways (e.g., Paystack or Flutterwave) for automated payment verification.

Implement advanced analytics and visual charts on the admin dashboard.

👩‍💻 Author
Mercy Ottah-Nelson Department of Computer Science, Lagos State University

Supervisor: Prof. Aribisala Benjamin
