// =====================
// rooms.js
// =====================

function fetchRooms() {
    fetch('/api/rooms', {
        credentials: 'include'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Network response was not ok");
        }
        return response.json();
    })
    .then(data => {
        console.log('Fetched rooms:', data);
        const table = document.getElementById('roomsTableBody');
        table.innerHTML = '';

        if (!Array.isArray(data)) {
            console.error("Expected array but got:", data);
            table.innerHTML = '<tr><td colspan="5">Invalid data format.</td></tr>';
            return;
        }

        if (data.length === 0) {
            table.innerHTML = '<tr><td colspan="5">No rooms found.</td></tr>';
        } else {
            data.forEach(room => {
                const row = `<tr>
                    <td>${room.room_id}</td>
                    <td>${room.hostel_name}</td>
                    <td>${room.room_number}</td>
                    <td>${room.capacity}</td>
                    <td>${room.current_occupants}</td>
                </tr>`;
                table.innerHTML += row;
            });
        }
    })
    .catch(error => {
        console.error('Error fetching rooms:', error);
        const table = document.getElementById('roomsTableBody');
        table.innerHTML = '<tr><td colspan="5">Error loading data.</td></tr>';
    });
}

// 🔁 Call the function when the DOM is ready
document.addEventListener('DOMContentLoaded', fetchRooms);

// The rest of the CRUD functions remain unchanged...

function addRoom(room) {
    fetch('/api/rooms', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(room)
    });
}

function updateRoom(id, room) {
    fetch(`/api/rooms/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(room)
    });
}

function deleteRoom(id) {
    fetch(`/api/rooms/${id}`, { method: 'DELETE' });
}
