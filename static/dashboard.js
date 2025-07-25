document.addEventListener("DOMContentLoaded", () => {
  fetchDashboardData();
});

function fetchDashboardData() {
  fetch("/api/dashboard", {
    credentials: 'include'
  })
    .then(response => {
      if (!response.ok) {
        throw new Error("Failed to fetch dashboard data");
      }
      return response.json();
    })
    .then(data => {
      document.getElementById("total-students").textContent = data.students;
      document.getElementById("total-rooms").textContent = data.rooms;
      document.getElementById("occupied-rooms").textContent = data.allocations;
      document.getElementById("total-payments").textContent = data.payments;
      document.getElementById("maintenance-issues").textContent = data.maintenance;
    })
    .catch(error => {
      console.error("Dashboard load error:", error);
      const boxes = document.querySelectorAll(".dashboard-card .value");
      boxes.forEach(box => box.textContent = "Error");
    });
}
