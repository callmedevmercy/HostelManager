// =====================
// allocations.js (REVISED)
// =====================

document.addEventListener("DOMContentLoaded", () => {
  fetchAllocations();
  fetchStudents();
  fetchHostels();

  document.getElementById("hostel-select").addEventListener("change", fetchRoomsByHostel);
  document.getElementById("allocation-form").addEventListener("submit", createAllocation);
});

// =====================
// FETCH ALLOCATIONS
// =====================
function fetchAllocations() {
  fetch("/api/allocations", { credentials: "include" })
    .then((response) => {
      if (!response.ok) throw new Error("Network response was not ok");
      return response.json();
    })
    .then((data) => {
      const tableBody = document.getElementById("allocations-table-body");
      tableBody.innerHTML = "";

      if (!Array.isArray(data) || data.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="6">No allocations found.</td></tr>';
        return;
      }

      data.forEach((allocation) => {
        const row = document.createElement("tr");
        row.innerHTML = `
          <td>${allocation.allocations_id}</td>
          <td>${allocation.name || allocation.student_name}</td>
          <td>${allocation.room_number}</td>
          <td>${allocation.hostel_name || "N/A"}</td>
          <td>${allocation.allocated_date || "N/A"}</td>
          <td>
            <button class="btn btn-primary btn-sm btn-edit me-2">Edit</button>
            <button class="btn btn-danger btn-sm btn-delete">Delete</button>
          </td>
        `;

        // DELETE HANDLER
        row.querySelector(".btn-delete").addEventListener("click", () => {
          if (confirm("Are you sure you want to delete this allocation?")) {
            fetch(`/api/allocations/${allocation.allocations_id}`, {
              method: "DELETE",
              credentials: "include",
            })
              .then((res) => {
                if (!res.ok) throw new Error("Delete failed");
                return res.json();
              })
              .then((result) => {
                alert(result.message || "Allocation deleted successfully.");
                row.remove();
              })
              .catch((err) => {
                console.error("Delete error:", err);
                alert("Failed to delete allocation.");
              });
          }
        });

        tableBody.appendChild(row);
      });
    })
    .catch((error) => {
      console.error("Fetch error:", error);
      const tableBody = document.getElementById("allocations-table-body");
      tableBody.innerHTML = '<tr><td colspan="6">Error loading data.</td></tr>';
    });
}

// =====================
// FETCH STUDENTS (Form)
// =====================
function fetchStudents() {
  fetch("/api/students", { credentials: "include" })
    .then((res) => res.json())
    .then((data) => {
      const studentSelect = document.getElementById("student-select");
      studentSelect.innerHTML = "";

      const defaultOption = document.createElement("option");
      defaultOption.value = "";
      defaultOption.textContent = "Select Student";
      defaultOption.disabled = true;
      defaultOption.selected = true;
      studentSelect.appendChild(defaultOption);

      data.forEach((student) => {
        const option = document.createElement("option");
        option.value = student.student_id;
        option.textContent = `${student.name} (${student.matric_number})`;
        studentSelect.appendChild(option);
      });
    });
}

// =====================
// FETCH HOSTELS & ROOMS
// =====================
function fetchHostels() {
  fetch("/api/rooms", { credentials: "include" })
    .then((res) => res.json())
    .then((data) => {
      const hostelSelect = document.getElementById("hostel-select");
      hostelSelect.innerHTML = "";

      const defaultOption = document.createElement("option");
      defaultOption.value = "";
      defaultOption.textContent = "Select Hostel";
      defaultOption.disabled = true;
      defaultOption.selected = true;
      hostelSelect.appendChild(defaultOption);

      const hostels = [...new Set(data.map((room) => room.hostel_name))];
      hostels.forEach((hostel) => {
        const option = document.createElement("option");
        option.value = hostel;
        option.textContent = hostel;
        hostelSelect.appendChild(option);
      });
    });
}


function fetchRoomsByHostel() {
  const selectedHostel = document.getElementById("hostel-select").value;
  const roomSelect = document.getElementById("room-select");
  roomSelect.innerHTML = "";

  const defaultOption = document.createElement("option");
  defaultOption.value = "";
  defaultOption.textContent = "Select Room";
  defaultOption.disabled = true;
  defaultOption.selected = true;
  roomSelect.appendChild(defaultOption);

  fetch("/api/rooms", { credentials: "include" })
    .then((res) => res.json())
    .then((data) => {
      const filteredRooms = data.filter((room) => room.hostel_name === selectedHostel);
      filteredRooms.forEach((room) => {
        const option = document.createElement("option");
        option.value = room.room_id;
        option.textContent = room.room_number;
        roomSelect.appendChild(option);
      });
    });
}

// =====================
// CREATE ALLOCATION
// =====================
function createAllocation(e) {
  e.preventDefault();
  const student_id = document.getElementById("student-select").value;
  const room_id = document.getElementById("room-select").value;
  const date_allocated = document.getElementById("date-allocated").value;

  fetch("/api/allocations", {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ student_id, room_id, date_allocated }),
  })
    .then((res) => {
      if (!res.ok) return res.json().then((err) => { throw new Error(err.error || "Allocation failed"); });
      return res.json();
    })
    .then((data) => {
      alert(data.message || "Allocation created!");
      fetchAllocations(); // Refresh table
      document.getElementById("allocation-form").reset();
      fetchStudents();     // Reset dropdowns
      fetchHostels();      // Reset dropdowns
      const roomSelect = document.getElementById("room-select");
      roomSelect.innerHTML = ""; // Clear rooms until a hostel is picked again
    })
    .catch((err) => {
      console.error("Create allocation error:", err);
      alert("Error: " + err.message);
    });
}

// =====================
// EDIT MODAL LOGIC
// =====================
document.addEventListener("DOMContentLoaded", () => {
  const tableBody = document.getElementById("allocations-table-body");

  tableBody.addEventListener("click", (e) => {
    if (e.target.classList.contains("btn-edit")) {
      const row = e.target.closest("tr");
      const allocationId = row.children[0].textContent;
      const studentName = row.children[1].textContent;
      const roomNumber = row.children[2].textContent;
      const hostelName = row.children[3].textContent;
      const date = row.children[4].textContent;

      document.getElementById("edit-allocation-id").value = allocationId;
      document.getElementById("edit-date-allocated").value = date;

      fetchStudentsForEdit(studentName);
      fetchHostelsForEdit(hostelName, roomNumber);

      const modal = new bootstrap.Modal(document.getElementById("editAllocationModal"));
      modal.show();
    }
  });

  document.getElementById("edit-hostel-select").addEventListener("change", () => {
    fetchRoomsForEdit(); // No preselect on manual change
  });

  document.getElementById("edit-allocation-form").addEventListener("submit", (e) => {
    e.preventDefault();
    const id = document.getElementById("edit-allocation-id").value;
    const student_id = document.getElementById("edit-student-select").value;
    const room_id = document.getElementById("edit-room-select").value;
    const date_allocated = document.getElementById("edit-date-allocated").value;

    fetch(`/api/allocations/${id}`, {
      method: "PUT",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ student_id, room_id, date_allocated }),
    })
      .then((res) => {
        if (!res.ok) throw new Error("Update failed");
        return res.json();
      })
      .then((data) => {
        alert(data.message || "Allocation updated.");
        bootstrap.Modal.getInstance(document.getElementById("editAllocationModal")).hide();
        fetchAllocations();
      })
      .catch((err) => {
        console.error("Update error:", err);
        alert("Failed to update allocation.");
      });
  });
});

// =====================
// EDIT MODAL HELPERS
// =====================
function fetchStudentsForEdit(selectedName = "") {
  fetch("/api/students", { credentials: "include" })
    .then((res) => res.json())
    .then((students) => {
      const select = document.getElementById("edit-student-select");
      select.innerHTML = "";

      const defaultOption = document.createElement("option");
      defaultOption.value = "";
      defaultOption.textContent = "Select Student";
      defaultOption.disabled = true;
      select.appendChild(defaultOption);

      students.forEach((student) => {
        const opt = document.createElement("option");
        opt.value = student.student_id;
        opt.textContent = `${student.name} (${student.matric_number})`;
        if (student.name === selectedName) opt.selected = true;
        select.appendChild(opt);
      });
    });
}

function fetchHostelsForEdit(selectedHostel = "", selectedRoom = "") {
  fetch("/api/rooms", { credentials: "include" })
    .then((res) => res.json())
    .then((rooms) => {
      const hostelSelect = document.getElementById("edit-hostel-select");
      const roomSelect = document.getElementById("edit-room-select");
      hostelSelect.innerHTML = "";
      roomSelect.innerHTML = "";

      const defaultHostelOption = document.createElement("option");
      defaultHostelOption.value = "";
      defaultHostelOption.textContent = "Select Hostel";
      defaultHostelOption.disabled = true;
      hostelSelect.appendChild(defaultHostelOption);

      const hostels = [...new Set(rooms.map((room) => room.hostel_name))];
      hostels.forEach((hostel) => {
        const opt = document.createElement("option");
        opt.value = hostel;
        opt.textContent = hostel;
        if (hostel === selectedHostel) opt.selected = true;
        hostelSelect.appendChild(opt);
      });

      fetchRoomsForEdit(selectedRoom);
    });
}

function fetchRoomsForEdit(preselectRoomNumber = "") {
  const hostel = document.getElementById("edit-hostel-select").value;
  fetch("/api/rooms", { credentials: "include" })
    .then((res) => res.json())
    .then((rooms) => {
      const select = document.getElementById("edit-room-select");
      select.innerHTML = "";

      const defaultRoomOption = document.createElement("option");
      defaultRoomOption.value = "";
      defaultRoomOption.textContent = "Select Room";
      defaultRoomOption.disabled = true;
      select.appendChild(defaultRoomOption);

      rooms
        .filter((room) => room.hostel_name === hostel)
        .forEach((room) => {
          const opt = document.createElement("option");
          opt.value = room.room_id;
          opt.textContent = room.room_number;
          if (room.room_number === preselectRoomNumber) opt.selected = true;
          select.appendChild(opt);
        });
    });
}
