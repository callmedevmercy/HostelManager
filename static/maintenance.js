document.addEventListener("DOMContentLoaded", () => {
    fetchMaintenance();

    const form = document.getElementById("maintenance-form"); // ✅ FIXED ID
    form.addEventListener("submit", handleFormSubmit);
});

function fetchMaintenance() {
    fetch("/api/maintenance")
        .then(res => res.json())
        .then(data => {
            console.log(data); // ✅ Check what's returned
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
                        <button class="btn btn-sm btn-primary" onclick="populateForm(
                            ${record.maintenance_id}, 
                            ${record.room_id}, 
                            \`${record.issue.replace(/`/g, "\\`")}\`, 
                            '${record.reported_on}', 
                            '${record.status}'
                        )">Edit</button>
                        <button class="btn btn-sm btn-danger" onclick="deleteRecord(${record.maintenance_id})">Delete</button>
                    </td>
                `;
                tbody.appendChild(row);
            });
        })
        .catch(err => {
            console.error("Error fetching maintenance data:", err);
        });
}

function populateForm(maintenance_id, room_id, issue_description, reported_on, status) {
    document.getElementById("issue_id").value = maintenance_id;
    document.getElementById("room_id").value = room_id;
    document.getElementById("issue_description").value = issue_description;

    if (reported_on) {
        const date = new Date(reported_on);
        if (!isNaN(date)) {
            const formattedDate = date.toISOString().split('T')[0];
            document.getElementById("date_reported").value = formattedDate;
        }
    }

    document.getElementById("status").value = status;
}

function handleFormSubmit(event) {
    event.preventDefault();
    const form = event.target;
    const issue_id = document.getElementById("issue_id").value;
    const payload = {
        room_id: parseInt(document.getElementById("room_id").value),
        issue_description: document.getElementById("issue_description").value,
        date_reported: document.getElementById("date_reported").value,
        status: document.getElementById("status").value
    };

      console.log("Submitting payload:", payload); // 👈 Add this
     
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
        document.getElementById("maintenance-form").reset(); // ✅ FIXED ID
        fetchMaintenance();
    })
    .catch(err => {
        console.error("Error:", err);
        alert("Failed to submit maintenance record");
    });
}

function deleteRecord(maintenance_id) {
    if (!confirm("Are you sure you want to delete this record?")) return;

    fetch(`/api/maintenance/${maintenance_id}`, {
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
document.addEventListener("DOMContentLoaded", () => {
    const addBtn = document.getElementById("addMaintenanceBtn");

    if (addBtn) {
        addBtn.addEventListener("click", () => {
            document.getElementById("maintenance-form").reset();
            document.getElementById("issue_id").value = ""; // ← Clears old ID
        });
    }
});
