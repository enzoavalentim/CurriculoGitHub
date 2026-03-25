document.getElementById("dev-name").textContent = dados.dev_name;
document.getElementById("dev-email").textContent = dados.email;
document.getElementById("dev-photo").src = dados.photo;

const languageIcons = {
  "Java": '<i class="devicon-java-plain-wordmark"></i>',
  "JavaScript": '<i class="devicon-javascript-plain"></i>',
  "Python": '<i class="devicon-python-plain-wordmark"></i>',
  "C": '<i class="devicon-c-original"></i>',
  "C++": '<i class="devicon-cplusplus-plain"></i>',
  "C#": '<i class="devicon-csharp-plain"></i>'
};

document.getElementById("main-language-icon").innerHTML =
  languageIcons[dados.main_language];

const highlight = document.querySelector(".dev-info-panel .info-highlight");
if (highlight && dados.specialization) {
  highlight.textContent = "Specialization:  " + dados.specialization;
}
 
const infoList = document.querySelector(".dev-info-panel .info-list");
if (infoList && dados.skills) {
  const skills = dados.skills.split(",").map(s => s.trim()).filter(Boolean).slice(0, 5);
  infoList.innerHTML = skills.map(s => `<li>${s}</li>`).join("");
}

