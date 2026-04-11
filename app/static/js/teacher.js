const courseSelect = document.getElementById("courseSelect");
const studentsTableBody = document.querySelector("#studentsTable tbody");
const gradeTableBody = document.querySelector("#gradeTable tbody");
const statsSummary = document.getElementById("statsSummary");
const ctx = document.getElementById("statsChart");
let chart;

function fillTables(students) {
  if (!students.length) {
    studentsTableBody.innerHTML = '<tr><td colspan="4" class="text-center text-muted">暂无选课学生</td></tr>';
    gradeTableBody.innerHTML = '<tr><td colspan="4" class="text-center text-muted">暂无可录入数据</td></tr>';
    return;
  }

  studentsTableBody.innerHTML = students.map((s) => `
    <tr>
      <td>${s.student_no}</td>
      <td>${s.name}</td>
      <td>${s.department}</td>
      <td>${s.grade === null ? "待录入" : s.grade}</td>
    </tr>
  `).join("");

  gradeTableBody.innerHTML = students.map((s) => `
    <tr>
      <td>${s.student_no}</td>
      <td>${s.name}</td>
      <td><input type="number" min="0" max="100" step="0.01" id="grade-${s.selection_id}" class="form-control form-control-sm" value="${s.grade ?? ""}"></td>
      <td><button class="btn btn-sm btn-primary" onclick="saveGrade(${s.selection_id})">保存</button></td>
    </tr>
  `).join("");
}

async function loadStudents(courseId) {
  const res = await fetch("/teacher/load_students", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ course_id: Number(courseId) }),
  });
  const data = await res.json();
  fillTables(data.students || []);
}

async function loadStats(courseId) {
  const res = await fetch(`/teacher/statistics?course_id=${courseId}`);
  const data = await res.json();

  const labels = data.segments.map((s) => s.range);
  const values = data.segments.map((s) => s.count);
  if (chart) chart.destroy();
  chart = new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [{ label: "人数", data: values }],
    },
  });

  statsSummary.innerHTML = `
    <div class="list-group-item">平均分：${data.avg_grade}</div>
    <div class="list-group-item">最高分：${data.max_grade}</div>
    <div class="list-group-item">最低分：${data.min_grade}</div>
    <div class="list-group-item">已录入人数：${data.count}</div>
  `;
}

window.saveGrade = async function saveGrade(selectionId) {
  const input = document.getElementById(`grade-${selectionId}`);
  const grade = Number(input.value);
  if (Number.isNaN(grade) || grade < 0 || grade > 100) {
    alert("成绩范围必须在 0-100。");
    return;
  }

  const res = await fetch("/teacher/save_grade", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ selection_id: selectionId, grade }),
  });
  const data = await res.json();
  alert(data.message || "保存完成");
  if (data.success && courseSelect.value) {
    await loadStudents(courseSelect.value);
    await loadStats(courseSelect.value);
  }
};

courseSelect?.addEventListener("change", async () => {
  if (!courseSelect.value) return;
  await loadStudents(courseSelect.value);
  await loadStats(courseSelect.value);
});

