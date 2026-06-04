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
