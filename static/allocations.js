// =====================
// allocations.js
// =====================

document.addEventListener("DOMContentLoaded", fetchAllocations);

function fetchAllocations() {
    fetch("/api/allocations", {
        credentials: "include"
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Network response was not ok");
        }
        return response.json();
    })
    .then(data => {
        const tableBody = document.getElementById("allocations-table-body");
        tableBody.innerHTML = "";

        if (!Array.isArray(data) || data.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="6">No allocations found.</td></tr>';
            return;
        }

        data.forEach(allocation => {
            const row = document.createElement("tr");

            row.innerHTML = `
                <td>${allocation.allocations_id}</td>
                <td>${allocation.name || allocation.student_name}</td>
                <td>${allocation.room_number}</td>
                <td>${allocation.hostel_name || "N/A"}</td>
                <td>${allocation.allocated_date || "N/A"}</td>
                <td><button class="btn btn-delete">Delete</button></td>
            `;

            const deleteBtn = row.querySelector(".btn-delete");
            deleteBtn.addEventListener("click", () => {
                if (confirm("Are you sure you want to delete this allocation?")) {
                    fetch(`/api/allocations/${allocation.allocations_id}`, {
                        method: "DELETE",
                        credentials: "include"
                    })
                    .then(res => {
                        if (!res.ok) throw new Error("Delete failed");
                        return res.json();
                    })
                    .then(result => {
                        alert(result.message || "Allocation deleted successfully.");
                        row.remove();
                    })
                    .catch(err => {
                        console.error("Delete error:", err);
                        alert("Failed to delete allocation.");
                    });
                }
            });

            tableBody.appendChild(row);
        });
    })
    .catch(error => {
        console.error("Fetch error:", error);
        const tableBody = document.getElementById("allocations-table-body");
        tableBody.innerHTML = '<tr><td colspan="6">Error loading data.</td></tr>';
    });
}
