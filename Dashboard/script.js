document.getElementById("dev-name").textContent = dados.dev_name;
document.getElementById("dev-email").textContent = dados.email;
document.getElementById("dev-photo").src = dados.photo;

// Ícones de linguagem
const languageIcons = {
  "Java":       '<i class="devicon-java-plain-wordmark"></i>',
  "JavaScript": '<i class="devicon-javascript-plain"></i>',
  "Python":     '<i class="devicon-python-plain-wordmark"></i>',
  "C":          '<i class="devicon-c-original"></i>',
  "Cpp":        '<i class="devicon-cplusplus-plain"></i>',
  "CSharp":     '<i class="devicon-csharp-plain"></i>'
};
document.getElementById("main-language-icon").innerHTML =
  languageIcons[dados.main_language] ?? "";

// ── Senioridade ────────────────────────────────────────────────────────────
let level = "Junior"; // valor padrão

if (dados.main_language == "Java") {
  if (dados.authoringFiles <= 145)
    level = "Junior";
  else if (dados.authoringFiles > 145 && dados.authoringFiles < 266)
    level = "Pleno";
  else
    level = "Senior";

} else if (dados.main_language == "JavaScript") {
  if (dados.authoringFiles <= 10)
    level = "Junior";
  else if (dados.authoringFiles > 10 && dados.authoringFiles < 100)
    level = "Pleno";
  else
    level = "Senior";

} else if (dados.main_language == "Python") {
  if (dados.authoringFiles <= 10)
    level = "Junior";
  else if (dados.authoringFiles > 10 && dados.authoringFiles < 100)
    level = "Pleno";
  else
    level = "Senior";

} else if (dados.main_language == "C") {
  if (dados.authoringFiles <= 10)
    level = "Junior";
  else if (dados.authoringFiles > 10 && dados.authoringFiles < 100)
    level = "Pleno";
  else
    level = "Senior";

} else if (dados.main_language == "Cpp") {
  if (dados.authoringFiles <= 10)
    level = "Junior";
  else if (dados.authoringFiles > 10 && dados.authoringFiles < 100)
    level = "Pleno";
  else
    level = "Senior";

} else if (dados.main_language == "CSharp") {
  if (dados.authoringFiles <= 10)
    level = "Junior";
  else if (dados.authoringFiles > 10 && dados.authoringFiles < 100)
    level = "Pleno";
  else
    level = "Senior";
}

// Atualiza o ícone de senioridade
const senioritySlot = document.getElementById("seniority-icon");
if (senioritySlot) {
  senioritySlot.innerHTML = `
    <img src="icons/${level}.svg" alt="${level}" title="${level}" width="60" />
  `;
}

// ── Informações do desenvolvedor ───────────────────────────────────────────
const highlight = document.querySelector(".dev-info-panel .info-highlight");
if (highlight && dados.specialization) {
  highlight.textContent = "Specialization: " + dados.specialization;
}

const infoList = document.querySelector(".dev-info-panel .info-list");
if (infoList && dados.skills) {
  const skills = dados.skills.split(",").map(s => s.trim()).filter(Boolean).slice(0, 5);
  infoList.innerHTML = skills.map(s => `<li>${s}</li>`).join("");
}