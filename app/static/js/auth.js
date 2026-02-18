
async function login() {
  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;
  const msg = document.getElementById('msg');

  try {
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

    if (!res.ok) throw await res.text();

    const data = await res.json();

    // simpan token
    localStorage.setItem('access_token', data.access_token);

    // redirect ke halaman ETD
    window.location.href = '/etd8a12';
  } catch (e) {
    msg.textContent = 'Login gagal';
  }
}
