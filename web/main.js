let currentScenario = "";

async function loadScenario() {
  const res = await fetch("/api/scenario");
  const data = await res.json();
  currentScenario = data.scenario;
  document.getElementById("scenario").textContent = currentScenario;
  document.getElementById("userInput").value = "";
  document.getElementById("output").textContent = "Awaiting evaluation...";
}

async function submitResponse() {
  const userText = document.getElementById("userInput").value.trim();
  if (!userText) return;

  document.getElementById("output").textContent = "Evaluating...";

  const res = await fetch("/api/evaluate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      scenario: currentScenario,
      response: userText
    })
  });

  const data = await res.json();
  const evaluation = data.evaluation || `[ERROR]: ${data.error}`;

  // Optional: separate score and feedback if needed
  const lines = evaluation.split("\n");
  const scoreLine = lines.find(line => line.startsWith("Score:"));
  const feedbackLine = lines.find(line => line.startsWith("Feedback:"));

  const formatted = (scoreLine && feedbackLine)
    ? `${scoreLine}\n\n${feedbackLine}`
    : evaluation;

  document.getElementById("output").textContent = formatted;
}

window.onload = loadScenario;
