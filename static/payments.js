// ==========================
// payments.js (Updated)
// ==========================

document.addEventListener("DOMContentLoaded", fetchPayments);

// GET all payments
function fetchPayments() {
    fetch("/api/payments", {
        credentials: 'include'
    })
    .then(res => {
        if (!res.ok) throw new Error("Network response was not ok");
        return res.json();
    })
    .then(data => {
        console.log("Fetched payments:", data);
        const tableBody = document.getElementById("paymentsTableBody");
        tableBody.innerHTML = "";

        if (!Array.isArray(data) || data.length === 0) {
            tableBody.innerHTML = "<tr><td colspan='8'>No payments found.</td></tr>";
            return;
        }

        data.forEach(p => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${p.payment_id}</td>
                <td>${p.student_name}</td>
                <td>${p.matric}</td>
                <td>${p.amount}</td>
                <td>${p.payment_date}</td>
                <td>${p.method}</td>
                <td>${p.purpose}</td>
                <td>${p.status}</td>
            `;
            tableBody.appendChild(row);
        });
    })
    .catch(error => {
        console.error("Error fetching payments:", error);
        const tableBody = document.getElementById("paymentsTableBody");
        tableBody.innerHTML = "<tr><td colspan='8'>Error loading data.</td></tr>";
    });
}

// POST new payment
function addPayment(payment) {
    fetch("/api/payments", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(payment)
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message || "Payment added.");
        fetchPayments();
    });
}

// PUT update payment
function updatePayment(id, payment) {
    fetch(`/api/payments/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(payment)
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message || "Payment updated.");
        fetchPayments();
    });
}

// DELETE payment
function deletePayment(id) {
    if (!confirm("Are you sure you want to delete this payment?")) return;

    fetch(`/api/payments/${id}`, {
        method: "DELETE",
        credentials: "include"
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message || "Payment deleted.");
        fetchPayments();
    });
}
