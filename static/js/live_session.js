// ===============================
// LIVE SESSION – PHASE 1 STEP 4
// ===============================

// ---------- AUTO JOIN ----------
fetch(`/api/session/join/${SESSION_LINK}`, {
    method: "POST"
})
.then(res => res.json())
.then(data => {
    console.log("Joined session:", data);
})
.catch(err => console.error(err));


// ---------- SESSION TIMER ----------
const timerEl = document.getElementById("sessionTimer");

// session start time from backend
const startTime = new Date(SESSION_STARTED_AT);

function updateTimer() {
    const now = new Date();
    const diff = Math.floor((now - startTime) / 1000);

    const minutes = String(Math.floor(diff / 60)).padStart(2, "0");
    const seconds = String(diff % 60).padStart(2, "0");

    timerEl.innerText = `${minutes}:${seconds}`;
}

setInterval(updateTimer, 1000);
updateTimer();


// ---------- LEAVE SESSION ----------
function leaveSession() {
    fetch(`/api/session/leave/${SESSION_LINK}`, {
        method: "POST"
    })
    .then(() => {
        window.location.href = "/student/dashboard";
    });
}

// student clicks Leave
const leaveBtn = document.getElementById("leaveSessionBtn");
if (leaveBtn) {
    leaveBtn.onclick = leaveSession;
}

// browser/tab closed → auto leave
window.addEventListener("beforeunload", () => {
    navigator.sendBeacon(
        `/api/session/leave/${SESSION_LINK}`
    );
});


// ---------- TEACHER: END SESSION ----------
const endBtn = document.getElementById("endSessionBtn");
if (endBtn) {
    endBtn.onclick = () => {
        if (!confirm("End this live session for all students?")) return;

        fetch(`/api/session/end/${SESSION_LINK}`, {
            method: "POST"
        })
        .then(() => {
            window.location.href = "/teacher/dashboard";
        });
    };
}
