// =====================
// rooms.js
// =====================

function fetchRooms() {
  fetch("/api/rooms", {
    credentials: "include",
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      return response.json();
    })
    .then((data) => {
      console.log("Fetched rooms:", data);
      const table = document.getElementById("roomsTableBody");
      table.innerHTML = "";

      if (!Array.isArray(data)) {
        console.error("Expected array but got:", data);
        table.innerHTML = '<tr><td colspan="5">Invalid data format.</td></tr>';
        return;
      }

      if (data.length === 0) {
        table.innerHTML = '<tr><td colspan="5">No rooms found.</td></tr>';
      } else {
        data.forEach((room) => {
          const row = `<tr>
                     <td>${room.room_id}</td>
                     <td>${room.hostel_name}</td>
                     <td>${room.room_number}</td>
                     <td>${room.capacity}</td>
                     <td>${room.current_occupants}</td>
                     <td>
                      <button class="btn btn-sm btn-warning me-1" onclick="startEdit(${room.room_id})">Edit</button>
                      <button class="btn btn-sm btn-danger" onclick="confirmDelete(${room.room_id}, '${room.hostel_name}', '${room.room_number}')">Delete</button>

                     </td>
                </tr>`;
          table.innerHTML += row;
        });
      }
    })
    .catch((error) => {
      console.error("Error fetching rooms:", error);
      const table = document.getElementById("roomsTableBody");
      table.innerHTML = '<tr><td colspan="5">Error loading data.</td></tr>';
    });
}

// 🔁 Call the function when the DOM is ready
document.addEventListener("DOMContentLoaded", fetchRooms);

// The rest of the CRUD functions remain unchanged...

function addRoom(room) {
  fetch("/api/rooms", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(room),
  });
}

function updateRoom(id, room) {
  fetch(`/api/rooms/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(room),
  });
}

function confirmDelete(roomId, hostelName, roomNumber) {
  const confirmed = confirm(`Are you sure you want to delete Room ${roomNumber} in ${hostelName}?`);
  if (confirmed) {
    deleteRoom(roomId);
  }
}

function deleteRoom(id) {
  fetch(`/api/rooms/${id}`, { method: "DELETE" });
}
fetch("/api/rooms/available", {
  credentials: "include",
})
  .then((res) => res.json())
  .then((data) => {
    const alertDiv = document.getElementById("noRoomsAlert");
    if (data.available === false) {
      alertDiv.classList.remove("d-none");
    } else {
      alertDiv.classList.add("d-none");
    }
  });
let editingRoomId = null;

document.addEventListener("DOMContentLoaded", () => {
  fetchRooms();
  checkRoomAvailability();

  document.getElementById("roomForm").addEventListener("submit", handleFormSubmit);
});


function addRoom(room) {
  fetch("/api/rooms", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(room),
    credentials: "include",
  }).then((res) => {
    if (res.ok) {
      fetchRooms(); // Refresh table
      checkRoomAvailability();
      document.getElementById("roomForm").reset(); // Clear form
    }
  });
}

function checkRoomAvailability() {
  fetch("/api/rooms/available", {
    credentials: "include",
  })
    .then((res) => res.json())
    .then((data) => {
      const alertDiv = document.getElementById("noRoomsAlert");
      if (data.available === false) {
        alertDiv.classList.remove("d-none");
      } else {
        alertDiv.classList.add("d-none");
      }
    });
}

function startEdit(id) {
  fetch(`/api/rooms`, { credentials: 'include' })
    .then(res => res.json())
    .then(data => {
      const room = data.find(r => r.room_id === id);
      if (room) {
        editingRoomId = id;
        document.getElementById('hostelName').value = room.hostel_name;
        document.getElementById('roomNumber').value = room.room_number;
        document.getElementById('capacity').value = room.capacity;
        document.getElementById('occupants').value = room.current_occupants;
      }
    });
}

function handleFormSubmit(event) {
    event.preventDefault();

    const roomData = {
        hostel_name: document.getElementById("hostelName").value,
        room_number: document.getElementById("roomNumber").value,
        capacity: document.getElementById("capacity").value,
        current_occupants: document.getElementById("occupants").value
    };

    if (editingRoomId) {
        // EDIT MODE: Send PUT request
        fetch(`/api/rooms/${editingRoomId}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(roomData)
        })
        .then(res => res.json())
        .then(() => {
            fetchRooms(); // Refresh
            document.getElementById("roomForm").reset();
            editingRoomId = null;
        });
    } else {
        // CREATE MODE: Send POST request
        fetch("/api/rooms", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(roomData)
        })
        .then(res => res.json())
        .then(() => {
            fetchRooms();
            document.getElementById("roomForm").reset();
        });
    }
}
