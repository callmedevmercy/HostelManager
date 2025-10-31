document.addEventListener("DOMContentLoaded", () => {
  fetchStudents();
  fetchPayments();

  const form = document.getElementById("paymentForm");
  if (form) {
    form.addEventListener("submit", handleFormSubmit);
  }
});

let editingPaymentId = null;

// Fetch students for dropdown
function fetchStudents() {
  fetch("/api/students", { credentials: "include" })
    .then((res) => res.json())
    .then((data) => {
      const studentSelect = document.getElementById("student_id");
      if (!studentSelect) return;

      studentSelect.innerHTML = '<option value="">Select Student</option>';

      data.forEach((student) => {
        const option = document.createElement("option");
        option.value = student.student_id;
        option.textContent = `${student.name} (${student.matric_number})`;
        studentSelect.appendChild(option);
      });
    })
    .catch((error) => {
      console.error("Error fetching students:", error);
    });
}

function refreshStudentDropdown() {
  fetchStudents();
  alert("Student list refreshed.");
}

function checkUnpaidStudents() {
  fetch("/api/students", { credentials: "include" })
    .then((res) => res.json())
    .then((students) => {
      fetch("/api/payments", { credentials: "include" })
        .then((res) => res.json())
        .then((payments) => {
          const paidStudentIds = new Set(payments.map((p) => p.student_id));
          const unpaidStudents = students.filter(
            (s) => !paidStudentIds.has(s.student_id)
          );

          if (unpaidStudents.length > 0) {
            alert(
              `${unpaidStudents.length} student(s) have not made any payments:\n\n` +
                unpaidStudents
                  .map((s) => `• ${s.name} (${s.matric_number})`)
                  .join("\n")
            );
          } else {
            alert("✅ All students have made payments.");
          }
        })
        .catch((err) => console.error("Error fetching payments:", err));
    })
    .catch((err) => console.error("Error fetching students:", err));
}

// Fetch all payments
function fetchPayments() {
  fetch("/api/payments", { credentials: "include" })
    .then((res) => {
      if (!res.ok) throw new Error("Network response was not ok");
      return res.json();
    })
    .then((data) => {
      console.log("Fetched payments:", data);
      const tableBody = document.getElementById("paymentsTableBody");
      if (!tableBody) return;

      tableBody.innerHTML = "";

      if (!Array.isArray(data) || data.length === 0) {
        tableBody.innerHTML =
          "<tr><td colspan='10'>No payments found.</td></tr>";
        return;
      }

      data.forEach((p) => {
        const row = document.createElement("tr");
        row.innerHTML = `
          <td>${p.payment_id}</td>
          <td>${p.student_name}</td>
          <td>${p.matric}</td>
          <td>₦${parseFloat(p.amount).toLocaleString()}</td>
          <td>${new Date(p.payment_date).toLocaleDateString()}</td>
          <td>${p.method}</td>
          <td>${p.purpose}</td>
          <td>${p.status}</td>
          <td>${p.receipt_no}</td>
          <td>
            <button class="btn btn-sm btn-warning" onclick="startEdit(
              ${p.payment_id}, 
              '${p.student_id}', 
              ${p.amount}, 
              '${p.payment_date}', 
              '${p.method}', 
              '${p.purpose}', 
              '${p.status}'
            )">Edit</button>
            <button class="btn btn-sm btn-danger" onclick="deletePayment(${p.payment_id})">Delete</button>
          </td>
        `;
        tableBody.appendChild(row);
      });
    })
    .catch((error) => {
      console.error("Error fetching payments:", error);
      const tableBody = document.getElementById("paymentsTableBody");
      if (tableBody) {
        tableBody.innerHTML =
          "<tr><td colspan='10'>Error loading data.</td></tr>";
      }
    });
}

// Handle form submit
function handleFormSubmit(event) {
  event.preventDefault();

  const payment = {
    student_id: document.getElementById("student_id").value,
    payment_method: document.getElementById("payment_method").value, // ✅ fixed
    amount: document.getElementById("amount").value,
    purpose: document.getElementById("purpose").value,
    status: document.getElementById("status").value,                 // use selected status
    receipt_no: document.getElementById("receipt_no") ? document.getElementById("receipt_no").value : null,
    payment_date: document.getElementById("payment_date").value      // send date if chosen
  };


  if (editingPaymentId) {
    updatePayment(editingPaymentId, payment);
    editingPaymentId = null;
  } else {
    addPayment(payment);
  }

  document.getElementById("paymentForm").reset();
}

// Add new payment
function addPayment(payment) {
  fetch("/api/payments", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify(payment),
  })
    .then((res) => res.json())
    .then((data) => {
      alert(data.message || "Payment added.");
      fetchPayments();
    });
}

// Update payment
function updatePayment(id, payment) {
  fetch(`/api/payments/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify(payment),
  })
    .then((res) => res.json())
    .then((data) => {
      alert(data.message || "Payment updated.");
      fetchPayments();
    });
}

// Delete payment
function deletePayment(id) {
  if (!confirm("Are you sure you want to delete this payment?")) return;

  fetch(`/api/payments/${id}`, {
    method: "DELETE",
    credentials: "include",
  })
    .then((res) => res.json())
    .then((data) => {
      alert(data.message || "Payment deleted.");
      fetchPayments();
    });
}

// Start editing a payment
function startEdit(
  payment_id,
  student_id,
  amount,
  payment_date,
  method,
  purpose,
  status
) {
  editingPaymentId = payment_id;

  fetch("/api/students", { credentials: "include" })
    .then((res) => res.json())
    .then((data) => {
      const studentSelect = document.getElementById("student_id");
      if (!studentSelect) return;

      studentSelect.innerHTML = '<option value="">Select Student</option>';

      data.forEach((student) => {
        const option = document.createElement("option");
        option.value = student.student_id;
        option.textContent = `${student.name} (${student.matric_number})`;
        studentSelect.appendChild(option);
      });

      studentSelect.value = student_id;
    })
    .catch((error) => {
      console.error("Error fetching students in edit:", error);
    });
  document.getElementById("payment_id").value = payment_id;
  document.getElementById("student_id").value = student_id;
  document.getElementById("amount").value = amount;
  document.getElementById("payment_date").value = new Date(payment_date)
    .toISOString()
    .split("T")[0];
  document.getElementById("method").value = method;
  document.getElementById("purpose").value = purpose;
  document.getElementById("status").value = status;

  window.scrollTo({ top: 0, behavior: "smooth" });
}
