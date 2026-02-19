const API = "http://127.0.0.1:5000"; // backend

let mode = "login";
let theme = "dark"; // Default to dark as requested
document.documentElement.setAttribute("data-theme", theme);

// --- Elements ---
const authOverlay = document.getElementById("authOverlay");
const closeAuth = document.getElementById("closeAuth");
const headerLoginBtn = document.getElementById("headerLoginBtn");
const headerRegisterBtn = document.getElementById("headerRegisterBtn");
const publicNav = document.getElementById("publicNav");
const privateNav = document.getElementById("privateNav");

// Dashboard Elements
const appContainer = document.getElementById("appContainer");
const docText = document.getElementById("docText");
const fileUpload = document.getElementById("fileUpload");
const analyzeBtn = document.getElementById("analyzeBtn");
const analysisResults = document.getElementById("analysisResults");
const emptyResult = document.getElementById("emptyResult");
const highlightContainer = document.getElementById("highlightedText");
const analysisStatus = document.getElementById("analysisStatus");
const tryBtn = document.getElementById("tryBtn");
const heroSection = document.getElementById("heroSection");

// Auth Form Elements
const authTitle = document.getElementById("authTitle");
const authSub = document.getElementById("authSub");
const nameBox = document.getElementById("nameBox");
const submitBtn = document.getElementById("submitBtn");
const switchBtn = document.getElementById("switchBtn");
const msg = document.getElementById("msg");
const userNameDisplay = document.getElementById("userName");
const historyOverlay = document.getElementById("historyOverlay");
const closeHistory = document.getElementById("closeHistory");
const historyList = document.getElementById("historyList");
const gaugeFill = document.getElementById("gaugeFill");
const complexityPercentage = document.getElementById("complexityPercentage");
const downloadPdfBtn = document.getElementById("downloadPdfBtn");

let currentUser = JSON.parse(localStorage.getItem("clauseEaseUser")) || null;

if (currentUser) {
  userNameDisplay.textContent = currentUser.name;
  publicNav.classList.add("hide");
  privateNav.classList.remove("hide");
}

// --- Helper Functions ---
function setMessage(text, ok = true) {
  msg.style.color = ok ? "var(--primary)" : "#ef4444";
  msg.textContent = text;
}

function showAuth(targetMode) {
  mode = targetMode;
  authOverlay.classList.remove("hide");
  if (mode === "login") {
    authTitle.textContent = "Login";
    authSub.textContent = "Access your simplified contracts.";
    submitBtn.textContent = "Login";
    nameBox.classList.add("hide");
    document.getElementById("switchText").innerHTML = 'Don\'t have an account? <span id="switchBtn">Register</span>';
  } else {
    authTitle.textContent = "Register";
    authSub.textContent = "Create a new account.";
    submitBtn.textContent = "Create Account";
    nameBox.classList.remove("hide");
    document.getElementById("switchText").innerHTML = 'Already have an account? <span id="switchBtn">Login</span>';
  }
  // Re-attach switchBtn listener
  document.getElementById("switchBtn").addEventListener("click", () => {
    showAuth(mode === "login" ? "register" : "login");
  });
}

// --- Event Listeners ---
headerLoginBtn.addEventListener("click", () => showAuth("login"));
headerRegisterBtn.addEventListener("click", () => showAuth("register"));
closeAuth.addEventListener("click", () => authOverlay.classList.add("hide"));

// Transition from Hero to App
tryBtn.addEventListener("click", () => {
  heroSection.classList.add("hide");
  appContainer.classList.remove("hide");
  window.scrollTo({ top: 0, behavior: "smooth" });
});

authOverlay.addEventListener("click", (e) => {
  if (e.target === authOverlay) authOverlay.classList.add("hide");
});

// Tab Switching
document.querySelectorAll(".tab-btn:not([data-subtab])").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab-btn:not([data-subtab])").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    const target = btn.dataset.tab;
    document.getElementById("pasteTab").classList.add("hide");
    document.getElementById("uploadTab").classList.add("hide");
    document.getElementById(`${target}Tab`).classList.remove("hide");
  });
});

// Sub-tab Switching for Preprocessing
document.querySelectorAll("[data-subtab]").forEach(btn => {
  btn.addEventListener("click", () => {
    const parent = btn.closest(".preprocessing-results");
    parent.querySelectorAll("[data-subtab]").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    const target = btn.dataset.subtab;
    parent.querySelector("#cleanedTextContent").classList.add("hide");
    parent.querySelector("#tokensContent").classList.add("hide");
    parent.querySelector(`#${target}Content`).classList.remove("hide");
  });
});

// Live Analysis Debounce
let analysisTimeout;
docText.addEventListener("input", () => {
  // Only auto-analyze if text is pasted or typed
  clearTimeout(analysisTimeout);
  analysisTimeout = setTimeout(() => {
    if (docText.value.trim().length > 10) {
      analyzeBtn.click();
    }
  }, 1000);
});

// File Upload Display
fileUpload.addEventListener("change", () => {
  const display = document.getElementById("fileNameDisplay");
  if (fileUpload.files.length > 0) {
    display.textContent = `📄 ${fileUpload.files[0].name}`;
    display.classList.remove("hide");
  } else {
    display.classList.add("hide");
  }
});

// Auth Logic
submitBtn.addEventListener("click", async () => {
  const name = document.getElementById("name")?.value?.trim();
  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value.trim();

  if (!email || !password || (mode === "register" && !name)) {
    setMessage("Please fill all required fields.", false);
    return;
  }

  setMessage("Processing...");

  try {
    if (mode === "register") {
      const res = await fetch(`${API}/api/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email, password })
      });
      const data = await res.json();
      if (!res.ok) return setMessage(data.message || "Register failed", false);
      setMessage("Registered ✅", true);
      setTimeout(() => showAuth("login"), 700);
      return;
    }

    // Login
    const res = await fetch(`${API}/api/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });
    const data = await res.json();
    if (!res.ok) return setMessage(data.message || "Login failed", false);

    setMessage("Login successful ✅", true);
    currentUser = data.user;
    localStorage.setItem("clauseEaseUser", JSON.stringify(currentUser));
    userNameDisplay.textContent = data.user.name;

    // UI Update
    setTimeout(() => {
      authOverlay.classList.add("hide");
      publicNav.classList.add("hide");
      privateNav.classList.remove("hide");
      setMessage("");
    }, 800);

  } catch (err) {
    setMessage("❌ Backend connection error", false);
  }
});

// Logout
document.getElementById("logoutBtn").addEventListener("click", () => {
  currentUser = null;
  localStorage.removeItem("clauseEaseUser");
  publicNav.classList.remove("hide");
  privateNav.classList.add("hide");
  // Optional: Reset analysis state
  emptyResult.classList.remove("hide");
  analysisResults.classList.add("hide");
});

// History Logic
userNameDisplay.addEventListener("click", async () => {
  if (!currentUser) return;
  historyOverlay.classList.remove("hide");
  historyList.innerHTML = "<p>Loading history...</p>";

  try {
    const res = await fetch(`${API}/api/history?email=${currentUser.email}`);
    const data = await res.json();

    if (data.length === 0) {
      historyList.innerHTML = '<p class="empty-history">No history found. Start analyzing to see your past reports.</p>';
      return;
    }

    historyList.innerHTML = "";
    data.forEach(item => {
      const div = document.createElement("div");
      div.className = "history-item";
      div.innerHTML = `
        <div class="history-info">
          <span class="history-preview">${item.text_preview}</span>
          <span class="history-meta">${new Date(item.created_at).toLocaleDateString()}</span>
        </div>
        <div class="history-scores">
          <span class="score-pill">FK: ${item.flesch_score.toFixed(1)}</span>
          <span class="score-pill">GF: ${item.fog_score.toFixed(1)}</span>
        </div>
      `;
      div.onclick = () => {
        docText.value = item.text_preview.replace("...", "");
        historyOverlay.classList.add("hide");
        analyzeBtn.click();
      };
      historyList.appendChild(div);
    });
  } catch (err) {
    historyList.innerHTML = "<p>Error loading history.</p>";
  }
});

closeHistory.onclick = () => historyOverlay.classList.add("hide");

// Analysis Logic
analyzeBtn.addEventListener("click", async () => {
  const text = docText.value.trim();
  const file = fileUpload.files[0];

  if (!text && !file) {
    alert("Please paste text or upload a file first.");
    return;
  }

  analyzeBtn.disabled = true;
  analyzeBtn.innerHTML = '<span class="btn-icon">⌛</span> Analyzing...';
  analysisStatus.textContent = "Analyzing...";
  document.querySelector(".status-dot").style.background = "var(--color-normal)";

  try {
    let res;
    if (file && !document.getElementById("uploadTab").classList.contains("hide")) {
      const formData = new FormData();
      formData.append("file", file);
      res = await fetch(`${API}/api/analyze`, {
        method: "POST",
        body: formData,
        headers: currentUser ? { "X-User-Email": currentUser.email } : {}
      });
    } else {
      res = await fetch(`${API}/api/analyze`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-User-Email": currentUser ? currentUser.email : ""
        },
        body: JSON.stringify({ text })
      });
    }

    const data = await res.json();
    if (!res.ok) throw new Error(data.message || "Analysis failed");

    // Display Results
    document.getElementById("fkGrade").textContent = data.readability.flesch_kincaid_grade.toFixed(1);
    document.getElementById("gfIndex").textContent = data.readability.gunning_fog.toFixed(1);
    document.getElementById("complexityLabel").textContent = data.complexity_label.split(" ")[0];

    // Update Gauge
    const fk = data.readability.flesch_reading_ease;
    // Flesch is 100 (simple) to 0 (complex). We want 0-100 complexity risk.
    const risk = Math.max(0, Math.min(100, 100 - fk));
    const rotation = (risk / 100) * 0.5; // 0.5 turns = 180deg
    gaugeFill.style.transform = `rotate(${0.5 + rotation}turn)`;
    complexityPercentage.textContent = `${Math.round(risk)}%`;

    // Store current analysis for PDF
    window.currentAnalysis = {
      text: data.original_text,
      flesch: data.readability.flesch_reading_ease.toFixed(1),
      fog: data.readability.gunning_fog.toFixed(1)
    };

    // Highlights
    highlightContainer.innerHTML = "";
    if (data.word_analysis) {
      data.word_analysis.forEach(word => {
        const span = document.createElement("span");
        span.textContent = word.text + " ";
        if (word.complexity !== "none") span.className = `word-${word.complexity}`;
        highlightContainer.appendChild(span);
      });
    }

    // Preprocessing Displays
    document.getElementById("cleanedTextOutput").textContent = data.cleaned_text;
    const sentenceList = document.getElementById("sentenceList");
    sentenceList.innerHTML = "";
    if (data.sentence_tokens) {
      data.sentence_tokens.forEach(sent => {
        const div = document.createElement("div");
        div.textContent = sent;
        sentenceList.appendChild(div);
      });
    }

    const wordList = document.getElementById("wordList");
    wordList.innerHTML = "";
    if (data.word_tokens) {
      data.word_tokens.forEach(word => {
        const span = document.createElement("span");
        span.textContent = word;
        wordList.appendChild(span);
      });
    }

    // Toggle View
    emptyResult.classList.add("hide");
    analysisResults.classList.remove("hide");
    document.querySelector(".analysis-section").classList.remove("hide");
    analysisStatus.textContent = "Complete";
    document.querySelector(".status-dot").style.background = "var(--primary)";

  } catch (err) {
    alert("❌ Error: " + err.message);
    analysisStatus.textContent = "Error";
    document.querySelector(".status-dot").style.background = "var(--color-complex)";
  } finally {
    analyzeBtn.disabled = false;
    analyzeBtn.innerHTML = '<span class="btn-icon">⚡</span> Analyze';
  }
});

// Theme Toggle (Simplified)
document.getElementById("themeToggle").addEventListener("click", () => {
  theme = theme === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", theme);
  document.getElementById("themeToggle").textContent = theme === "dark" ? "☀️" : "🌓";
});

// PDF Export
downloadPdfBtn.addEventListener("click", async () => {
  if (!window.currentAnalysis) return;

  downloadPdfBtn.disabled = true;
  downloadPdfBtn.innerHTML = "Generating...";

  try {
    const res = await fetch(`${API}/api/export-pdf`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(window.currentAnalysis)
    });
    const data = await res.json();
    if (res.ok) {
      alert("Analysis Report Generated! Opening in new tab...");
      window.open(`${API}/uploads/${data.filename}`, "_blank");
    } else {
      alert("Export failed: " + data.message);
    }
  } catch (err) {
    alert("Export error occurred.");
  } finally {
    downloadPdfBtn.disabled = false;
    downloadPdfBtn.innerHTML = '<span class="btn-icon">📄</span> Download Analysis (PDF)';
  }
});
