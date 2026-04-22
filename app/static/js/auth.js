async function login() {
  const username = document.getElementById('username').value.trim();
  const password = document.getElementById('password').value.trim();
  const msg = document.getElementById('msg');
  const btn = document.querySelector("button");

  msg.textContent = "";

  if (!username || !password) {
    msg.textContent = "Username dan password wajib diisi";
    return;
  }

  try {
    btn.innerText = "Loading...";
    btn.disabled = true;

    const form = new URLSearchParams();
    form.append('username', username);
    form.append('password', password);

    const res = await fetch('/auth/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: form
    });

    if (!res.ok) {
      throw new Error("Username atau password salah");
    }

    const data = await res.json();
    localStorage.setItem('access_token', data.access_token);

    window.location.href = '/devices';

  } catch (e) {
    msg.textContent = e.message;
  } finally {
    btn.innerText = "Login";
    btn.disabled = false;
  }
}
