const API = "http://localhost:5000"; // backend

let mode = "login";

const title = document.getElementById("title");
const sub = document.getElementById("sub");
const nameBox = document.getElementById("nameBox");
const submitBtn = document.getElementById("submitBtn");
const switchBtn = document.getElementById("switchBtn");
const switchText = document.getElementById("switchText");
const msg = document.getElementById("msg");

function setMessage(text, ok = true) {
  msg.style.color = ok ? "#059669" : "#dc2626";
  msg.textContent = text;
}

switchBtn.addEventListener("click", () => {
  setMessage("");
  if (mode === "login") {
    mode = "register";
    title.textContent = "Register";
    sub.textContent = "Create a new account (saved in MySQL database).";
    submitBtn.textContent = "Create Account";
    nameBox.classList.remove("hide");
    switchText.textContent = "Already have an account?";
    switchBtn.textContent = "Login";
  } else {
    mode = "login";
    title.textContent = "Login";
    sub.textContent = "Login using your registered email and password.";
    submitBtn.textContent = "Login";
    nameBox.classList.add("hide");
    switchText.textContent = "Don't have an account?";
    switchBtn.textContent = "Register";
  }
});

submitBtn.addEventListener("click", async () => {
  const name = document.getElementById("name")?.value?.trim();
  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value.trim();

  if (!email || !password || (mode === "register" && !name)) {
    setMessage("Please fill all required fields.", false);
    return;
  }

  setMessage("Please wait...");

  try {
    if (mode === "register") {
      const res = await fetch(`${API}/api/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email, password })
      });

      const data = await res.json();
      if (!res.ok) return setMessage(data.message || "Register failed", false);

      setMessage(data.message || "Registered ✅", true);
      setTimeout(() => switchBtn.click(), 700);
      return;
    }

    // login
    const res = await fetch(`${API}/api/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });

    const data = await res.json();
    if (!res.ok) return setMessage(data.message || "Login failed", false);

    setMessage(data.message || "Login successful ✅", true);
  } catch (err) {
    setMessage("❌ Backend not running / connection blocked", false);
  }
});
