document.addEventListener("DOMContentLoaded", () => {
    fetchMaintenance();

    const form = document.getElementById("maintenanceForm");
    form.addEventListener("submit", handleFormSubmit);
});

function fetchMaintenance() {
    fetch("/api/maintenance")
        .then(res => res.json())
        .then(data => {
          console.log(data); // 👈 ADD THIS LINE
            const tbody = document.getElementById("maintenance-table");
            tbody.innerHTML = "";

            data.forEach(record => {
                const row = document.createElement("tr");

                row.innerHTML = `
                    <td>${record.maintenance_id}</td>
                    <td>${record.room_id}</td>
                    <td>${record.issue}</td>
                    <td>${new Date(record.reported_on).toLocaleDateString()}</td>
                    <td>${record.status}</td>
                    <td>
                        <button class="btn btn-sm btn-primary" onclick="populateForm(${record.issue_id}, ${record.room_id}, '${record.issue_description}', '${record.date_reported}', '${record.status}')">Edit</button>
                        <button class="btn btn-sm btn-danger" onclick="deleteRecord(${record.issue_id})">Delete</button>
                    </td>
                `;
                tbody.appendChild(row);
            });
        })
        .catch(err => {
            console.error("Error fetching maintenance data:", err);
        });
}

function populateForm(issue_id, room_id, issue_description, date_reported, status) {
    document.getElementById("issue_id").value = issue_id;
    document.getElementById("room_id").value = room_id;
    document.getElementById("issue_description").value = issue_description;
    document.getElementById("date_reported").value = date_reported.slice(0, 10);
    document.getElementById("status").value = status;
}

function handleFormSubmit(event) {
    event.preventDefault();

    const issue_id = document.getElementById("issue_id").value;
    const payload = {
        room_id: parseInt(document.getElementById("room_id").value),
        issue_description: document.getElementById("issue_description").value,
        date_reported: document.getElementById("date_reported").value,
        status: document.getElementById("status").value
    };

    const url = issue_id ? `/api/maintenance/${issue_id}` : "/api/maintenance";
    const method = issue_id ? "PUT" : "POST";

    fetch(url, {
        method: method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    })
    .then(res => {
        if (!res.ok) throw new Error("Failed to submit maintenance record");
        return res.json();
    })
    .then(() => {
        document.getElementById("maintenanceForm").reset();
        fetchMaintenance();
    })
    .catch(err => {
        console.error("Error:", err);
        alert("Failed to submit maintenance record");
    });
}

function deleteRecord(issue_id) {
    if (!confirm("Are you sure you want to delete this record?")) return;

    fetch(`/api/maintenance/${issue_id}`, {
        method: "DELETE"
    })
    .then(res => {
        if (!res.ok) throw new Error("Failed to delete maintenance record");
        return res.json();
    })
    .then(() => {
        fetchMaintenance();
    })
    .catch(err => {
        console.error("Error:", err);
        alert("Failed to delete maintenance record");
    });
}
