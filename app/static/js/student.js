async function postAction(url, courseId, confirmText) {
  if (!confirm(confirmText)) return;
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ course_id: courseId }),
  });
  const data = await res.json();
  alert(data.message || "操作完成");
  if (data.success) {
    location.reload();
  }
}

document.querySelectorAll(".action-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    const courseId = btn.dataset.courseId;
    const action = btn.dataset.action;
    if (action === "select") {
      postAction("/student/select_course", courseId, "确认选择该课程？");
    } else {
      postAction("/student/drop_course", courseId, "确认退课？退课后不可恢复。");
    }
  });
});



const syllabusModal = document.getElementById("syllabusModal");
syllabusModal?.addEventListener("show.bs.modal", (event) => {
  const trigger = event.relatedTarget;
  if (!trigger) return;
  const title = document.getElementById("syllabusModalTitle");
  const body = document.getElementById("syllabusModalBody");
  title.textContent = (trigger.dataset.courseName || "课程") + " — 大纲";
  body.textContent = trigger.dataset.syllabus || "（暂未填写大纲）";
});


document.querySelectorAll(".lesson-btn").forEach((btn) => {
  btn.addEventListener("click", async () => {
    const courseId = btn.dataset.courseId;
    const courseName = btn.dataset.courseName;
    const tbody = document.querySelector("#lessonsModalTable tbody");
    document.getElementById("lessonsModalTitle").textContent = courseName + " — 教学进度";
    tbody.innerHTML = '<tr><td colspan="3" class="text-center text-muted">加载中…</td></tr>';
    new bootstrap.Modal(document.getElementById("lessonsModal")).show();
    const res = await fetch("/student/lessons", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ course_id: Number(courseId) }),
    });
    const data = await res.json();
    if (!data.lessons || !data.lessons.length) {
      tbody.innerHTML = '<tr><td colspan="3" class="text-center text-muted">教师尚未发布教学进度</td></tr>';
      return;
    }
    const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
    tbody.innerHTML = data.lessons.map((l) => `<tr><td>第 ${l.week} 周</td><td>${esc(l.topic)}</td><td>${esc(l.note || "")}</td></tr>`).join("");
  });
});
