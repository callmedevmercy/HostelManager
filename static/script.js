/*
==========================================================
= Wait for the entire HTML content to be fully loaded    =
==========================================================
*/
document.addEventListener("DOMContentLoaded", () => {

    /*
    ===============================================
    = Fetch student data from the Flask backend   =
    ===============================================
    */
    fetch("/students")
        .then(response => response.json())  // Convert the response to JSON
        .then(data => {
            /*
            =====================================================
            = Get the div where student data will be displayed  =
            =====================================================
            */
            const studentList = document.getElementById("student-list");

            // Clear the "Loading students..." placeholder
            studentList.innerHTML = "";

            /*
            =========================================
            = If no students are found, show a note =
            =========================================
            */
            if (data.length === 0) {
                studentList.innerHTML = "<p>No students found.</p>";
                return;
            }

            /*
            =======================================
            = Create a list of student <li> items =
            =======================================
            */
            const ul = document.createElement("ul");

            data.forEach(student => {
                const li = document.createElement("li");
                li.textContent = `${student.name} (${student.matric}) - ${student.department}`;
                ul.appendChild(li);
            });

            // Add the list to the DOM
            studentList.appendChild(ul);
        })
        .catch(error => {
            /*
            ============================================
            = If there's an error, show a message on UI =
            ============================================
            */
            console.error("Error fetching students:", error);
            document.getElementById("student-list").innerHTML = "<p>Error loading students.</p>";
        });
});
