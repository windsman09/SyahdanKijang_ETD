async function login() {
  const username = document.getElementById('username').value.trim();
  const password = document.getElementById('password').value.trim();
  const msg = document.getElementById('msg');
  const btn = document.querySelector("button");

  // reset message
  msg.textContent = "";

  // validasi sederhana
  if (!username || !password) {
    msg.textContent = "Username dan password wajib diisi";
    return;
  }

  try {
    // loading state
    btn.innerText = "Loading...";
    btn.disabled = true;

    const form = new URLSearchParams();
    form.append('username', username);
    form.append('password', password);

    const res = await fetch('/auth/token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: form
    });

    if (!res.ok) {
      const errorText = await res.text();
      throw new Error(errorText || "Login gagal");
    }

    const data = await res.json();

    // simpan token
    localStorage.setItem('access_token', data.access_token);

    // redirect
    window.location.href = '/etd8a12';

  } catch (e) {
    msg.textContent = "Login gagal: " + e.message;
  } finally {
    btn.innerText = "Login";
    btn.disabled = false;
  }
}
