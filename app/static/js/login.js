document.getElementById("loginForm")?.addEventListener("submit", (event) => {
  const form = event.target;
  const username = form.username.value.trim();
  const password = form.password.value.trim();
  if (!username || !password) {
    event.preventDefault();
    alert("用户名和密码不能为空。");
  }
});

