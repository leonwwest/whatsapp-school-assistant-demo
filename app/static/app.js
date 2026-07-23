const form = document.querySelector("#message-form");
const input = document.querySelector("#message");
const chat = document.querySelector("#chat");
const trace = document.querySelector("#trace");
const runState = document.querySelector("#run-state");
const resultCard = document.querySelector("#result-card");
const intent = document.querySelector("#intent");
const confidence = document.querySelector("#confidence");
const source = document.querySelector("#source");

const now = () =>
  new Intl.DateTimeFormat("de-DE", {
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date());

function addMessage(text, role, warning = false) {
  const bubble = document.createElement("div");
  bubble.className = `message ${role}${warning ? " warning" : ""}`;
  bubble.textContent = text;

  const time = document.createElement("time");
  time.textContent = now();
  bubble.append(time);
  chat.append(bubble);
  chat.scrollTop = chat.scrollHeight;
  return bubble;
}

function addTyping() {
  const bubble = document.createElement("div");
  bubble.className = "message assistant typing";
  bubble.setAttribute("aria-label", "Assistent schreibt");
  bubble.innerHTML = "<i></i><i></i><i></i>";
  chat.append(bubble);
  chat.scrollTop = chat.scrollHeight;
  return bubble;
}

function resetTrace() {
  const labels = [
    ["Webhook", "Nachricht wird angenommen"],
    ["Intent & Kontext", "Anfrage wird eingeordnet"],
    ["Grounded AI", "Quelle wird abgerufen"],
    ["Safety & Handoff", "Antwort wird geprüft"],
  ];

  trace.innerHTML = labels
    .map(
      ([name, detail], index) => `
        <li class="idle">
          <span>${index + 1}</span>
          <div><strong>${name}</strong><small>${detail}</small></div>
        </li>
      `,
    )
    .join("");
}

function compactTrace(steps) {
  const groups = [
    steps.filter((step) =>
      ["Webhook", "Normalisierung"].includes(step.name),
    ),
    steps.filter((step) =>
      ["Intent-Erkennung", "Wissensabruf"].includes(step.name),
    ),
    steps.filter((step) => step.name === "KI-Antwort"),
    steps.filter((step) =>
      ["Sicherheitsprüfung", "Übergabe"].includes(step.name),
    ),
  ];

  const labels = ["Webhook", "Intent & Kontext", "Grounded AI", "Safety & Handoff"];

  return groups.map((group, index) => {
    const last = group.at(-1);
    const status = group.some((step) =>
      ["blocked", "human"].includes(step.status),
    )
      ? "human"
      : group.length
        ? "done"
        : "idle";

    return {
      label: labels[index],
      detail: last?.detail ?? "Nicht erforderlich",
      status,
    };
  });
}

async function animateTrace(steps) {
  const grouped = compactTrace(steps);
  const items = [...trace.querySelectorAll("li")];

  for (let index = 0; index < items.length; index += 1) {
    await new Promise((resolve) => window.setTimeout(resolve, 230));
    items[index].className = grouped[index].status;
    items[index].querySelector("small").textContent = grouped[index].detail;
  }
}

async function sendMessage(message) {
  addMessage(message, "user");
  resetTrace();
  resultCard.classList.add("hidden");
  runState.textContent = "Verarbeitung";
  runState.classList.add("running");
  const typing = addTyping();

  try {
    const response = await fetch("/api/messages", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: "portfolio-demo", message }),
    });

    if (!response.ok) {
      throw new Error(`API-Fehler ${response.status}`);
    }

    const data = await response.json();
    await animateTrace(data.trace);
    typing.remove();
    addMessage(data.reply, "assistant", data.escalated);

    intent.textContent = data.intent;
    confidence.textContent = `${Math.round(data.confidence * 100)} %`;
    source.textContent = data.source;
    resultCard.classList.remove("hidden");
    runState.textContent = data.escalated ? "Übergeben" : "Beantwortet";
  } catch (error) {
    typing.remove();
    addMessage(
      "Die lokale Demo-API ist gerade nicht erreichbar. Bitte Server neu starten.",
      "assistant",
      true,
    );
    runState.textContent = "Fehler";
    console.error(error);
  } finally {
    runState.classList.remove("running");
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = input.value.trim();
  if (!message) return;
  input.value = "";
  input.disabled = true;
  await sendMessage(message);
  input.disabled = false;
  input.focus();
});

document.querySelectorAll("[data-prompt]").forEach((button) => {
  button.addEventListener("click", () => {
    input.value = button.dataset.prompt;
    form.requestSubmit();
  });
});

