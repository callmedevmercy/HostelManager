let editingStudentId = null; // track which student is being edited

function fetchStudents() {
  fetch("/api/students", { credentials: "include" })
    .then((response) => {
      if (!response.ok) throw new Error("Network response was not ok");
      return response.json();
    })
    .then((data) => {
      const table = document.getElementById("studentsTableBody");
      table.innerHTML = "";

      if (!Array.isArray(data)) {
        table.innerHTML = '<tr><td colspan="7">Invalid data format.</td></tr>';
        return;
      }

      if (data.length === 0) {
        table.innerHTML = '<tr><td colspan="7">No students found.</td></tr>';
      } else {
        data.forEach((student) => {
          const row = `
            <tr>
              <td>${student.student_id}</td>
              <td>${student.name}</td>
              <td>${student.matric_number}</td>
              <td>${student.department}</td>
              <td>${student.level}</td>
              <td>${student.gender}</td>
              <td>
                <button class="btn btn-warning btn-sm" onclick='editStudent(${JSON.stringify(
                  student
                )})'>Edit</button>
                <button class="btn btn-danger btn-sm" onclick="deleteStudent(${student.student_id})">Delete</button>
              </td>
            </tr>`;
          table.innerHTML += row;
        });
      }
    })
    .catch((error) => {
      console.error("Error fetching students:", error);
      const table = document.getElementById("studentsTableBody");
      table.innerHTML = '<tr><td colspan="7">Error loading data.</td></tr>';
    });
}

function handleFormSubmit(event) {
  event.preventDefault();

  const student = {
    name: document.getElementById("name").value,
    matric_number: document.getElementById("matric_number").value,
    department: document.getElementById("department").value,
    level: parseInt(document.getElementById("level").value),
    gender: document.getElementById("gender").value,
  };

  if (editingStudentId) {
    // 🔄 Update existing student
    fetch(`/api/students/${editingStudentId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify(student),
    })
      .then((res) => {
        if (!res.ok) throw new Error("Failed to update student.");
        return res.json();
      })
      .then(() => {
        alert("Student updated successfully!");
        editingStudentId = null; // reset
        document.getElementById("studentForm").reset();
        fetchStudents();
      })
      .catch((err) => console.error("Error updating student:", err));
  } else {
    // ➕ Add new student
    fetch("/api/students", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify(student),
    })
      .then((res) => {
        if (!res.ok) throw new Error("Failed to add student.");
        return res.json();
      })
      .then(() => {
        alert("Student added successfully!");
        document.getElementById("studentForm").reset();
        fetchStudents();
      })
      .catch((err) => console.error("Error adding student:", err));
  }
}

function deleteStudent(studentId) {
  if (!confirm("Are you sure you want to delete this student?")) return;

  fetch(`/api/students/${studentId}`, {
    method: "DELETE",
    credentials: "include",
  })
    .then(async (res) => {
      const data = await res.json();

      if (res.ok) {
        // ✅ Student deleted successfully
        alert(data.message || "Student deleted successfully!");
        fetchStudents();
      } else {
        // ❌ Error from backend (e.g., student still has allocations)
        alert(data.error || "Failed to delete student. Please try again.");
      }
    })
    .catch((err) => {
      console.error("Error deleting student:", err);
      alert("An unexpected error occurred. Please try again.");
    });
}



function editStudent(student) {
  editingStudentId = student.student_id; // track current editing ID
  document.getElementById("name").value = student.name;
  document.getElementById("matric_number").value = student.matric_number;
  document.getElementById("department").value = student.department;
  document.getElementById("level").value = student.level;
  document.getElementById("gender").value = student.gender;

  // Change button text to "Update"
  document.querySelector("#studentForm button[type='submit']").textContent =
    "Update Student";
}

// Reset form to Add mode
function resetForm() {
  editingStudentId = null;
  document.getElementById("studentForm").reset();
  document.querySelector("#studentForm button[type='submit']").textContent =
    "Save Student";
}

document.addEventListener("DOMContentLoaded", () => {
  fetchStudents();
  document.getElementById("studentForm").addEventListener("submit", handleFormSubmit);
});
