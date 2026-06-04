const dataEl = document.getElementById("adminStatsData");
if (dataEl) {
  const data = JSON.parse(dataEl.textContent);

  function bar(id, labels, datasets, opts) {
    const el = document.getElementById(id);
    if (!el) return;
    new Chart(el, {
      type: "bar",
      data: { labels, datasets },
      options: Object.assign({
        responsive: true,
        plugins: { legend: { position: "top" } },
        scales: { y: { beginAtZero: true } },
      }, opts || {}),
    });
  }

  // 1) 学生选课情况：每门课的人数 vs 容量
  bar("enrollChart",
    data.courses.map((c) => c.label),
    [
      { label: "已选人数", data: data.courses.map((c) => c.selected), backgroundColor: "rgba(54, 162, 235, 0.7)" },
      { label: "容量",     data: data.courses.map((c) => c.capacity), backgroundColor: "rgba(201, 203, 207, 0.5)" },
    ]);

  // 2) 教师授课情况
  bar("teachingChart",
    data.teachers.map((t) => t.label),
    [
      { label: "授课门数",   data: data.teachers.map((t) => t.course_count),  backgroundColor: "rgba(75, 192, 192, 0.7)" },
      { label: "选课学生人次", data: data.teachers.map((t) => t.student_count), backgroundColor: "rgba(255, 159, 64, 0.7)" },
    ]);

  // 3) 成绩分布：堆叠柱图
  bar("gradeChart",
    data.grades.map((g) => g.label),
    [
      { label: "0-59",   data: data.grades.map((g) => g.fail),      backgroundColor: "rgba(220, 53, 69, 0.7)",   stack: "a" },
      { label: "60-69",  data: data.grades.map((g) => g.pass),      backgroundColor: "rgba(255, 193, 7, 0.7)",   stack: "a" },
      { label: "70-79",  data: data.grades.map((g) => g.mid),       backgroundColor: "rgba(13, 202, 240, 0.7)",  stack: "a" },
      { label: "80-89",  data: data.grades.map((g) => g.good),      backgroundColor: "rgba(25, 135, 84, 0.7)",   stack: "a" },
      { label: "90-100", data: data.grades.map((g) => g.excellent), backgroundColor: "rgba(13, 110, 253, 0.7)",  stack: "a" },
    ],
    { scales: { x: { stacked: true }, y: { stacked: true, beginAtZero: true } } });

  // 4) 学分完成情况
  bar("creditChart",
    data.credits.map((s) => s.label),
    [
      { label: "已获学分", data: data.credits.map((s) => s.credits), backgroundColor: "rgba(102, 16, 242, 0.7)" },
    ]);
}
