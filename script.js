const message = document.getElementById("message");

function showMessage(text) {
  message.className = "message";
  message.textContent = text;
}

async function registerStudent() {
  const name = document.getElementById("name").value.trim();
  const roll_no = document.getElementById("roll").value.trim();

  if (!name || !roll_no) {
    alert("Enter student name and roll number.");
    return;
  }

  showMessage("Registering student and opening camera...");

  try {
    const res = await fetch("/api/register", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({name, roll_no})
    });
    const data = await res.json();
    showMessage(data.message);
    if (data.success) {
      document.getElementById("name").value = "";
      document.getElementById("roll").value = "";
    }
  } catch (err) {
    showMessage("Error: " + err.message);
  }
}

async function trainModel() {
  showMessage("Training face model...");
  const res = await fetch("/api/train", {method:"POST"});
  const data = await res.json();
  showMessage(data.message);
}

async function startAttendance() {
  showMessage("Starting camera...");
  const res = await fetch("/api/start", {method:"POST"});
  const data = await res.json();
  showMessage(data.message);
  setTimeout(loadAttendance, 1000);
}

async function loadAttendance() {
  try {
    const res = await fetch("/api/attendance");
    const data = await res.json();
    const body = document.getElementById("attendanceBody");
    body.innerHTML = "";

    if (!data.success) {
      showMessage(data.message);
      return;
    }

    data.data.forEach(row => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${row.roll_no}</td>
        <td>${row.name}</td>
        <td>${row.attendance_date}</td>
        <td>${row.attendance_time}</td>
      `;
      body.appendChild(tr);
    });
  } catch (err) {
    showMessage("Could not load attendance. Check MySQL/server.");
  }
}

loadAttendance();
setInterval(loadAttendance, 5000);
