function fetchStudents() {
    fetch('/api/students', {
        credentials: 'include'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Network response was not ok");
        }
        return response.json();
    })
    .then(data => {
        console.log('Fetched students:', data);
        const table = document.getElementById('studentsTableBody');
        table.innerHTML = '';

        if (!Array.isArray(data)) {
            console.error("Expected array but got:", data);
            table.innerHTML = '<tr><td colspan="6">Invalid data format.</td></tr>';
            return;
        }

        if (data.length === 0) {
            table.innerHTML = '<tr><td colspan="6">No students found.</td></tr>';
        } else {
            data.forEach(student => {
                const row = `<tr>
                    <td>${student.student_id}</td>
                    <td>${student.name}</td>
                    <td>${student.matric_number}</td>
                    <td>${student.department}</td>
                    <td>${student.level}</td>
                    <td>${student.gender}</td>
                </tr>`;
                table.innerHTML += row;
            });
        }
    })
    .catch(error => {
        console.error('Error fetching students:', error);
        const table = document.getElementById('studentsTableBody');
        table.innerHTML = '<tr><td colspan="6">Error loading data.</td></tr>';
    });
}

// 🔁 Call the function when the DOM is ready
document.addEventListener('DOMContentLoaded', fetchStudents);
