let SKILLS_URL = "http://127.0.0.1:8000/get_skills";

function fetchSkills(endpointUrl) {
    return fetch(endpointUrl)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status} - ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            return loadSkills(data)
        })
        .catch(error => {
            console.error('Error fetching skills:', error.message || error);
            throw error;
        });
}

function resetAddSkillModal() {
    document.getElementById("searchSkillInput").value = "";
    document.getElementById("skillNameSelect").innerHTML = "";
    document.getElementById("skillLevelSelect").value = "";

    document.getElementById("beginner").classList.remove("active");
    document.getElementById("intermediate").classList.remove("active");
    document.getElementById("advanced").classList.remove("active");

    document.getElementById("skillNameFeedback").style.display = "none";
    document.getElementById("skillLevelFeedback").style.display = "none";
}

function hideModal() {
    let addSkillModalElement = document.getElementById("addSkillModal");
    let addSkillModal = bootstrap.Modal.getInstance(addSkillModalElement);
    addSkillModal.hide();
}

function showError(fieldId) {
    let errorMessage = document.getElementById(fieldId);
    errorMessage.style.display = 'block';
}

function hideError(fieldId) {
    let errorMessage = document.getElementById(fieldId);
    errorMessage.style.display = 'none';
}

function loadSkills(skills) {
    const selectElement = document.getElementById('skillNameSelect');
    for (let i = 0; i < skills.length; i++) {
        const newOption = document.createElement('option');
        let skill = skills[i];
        newOption.value = skill.id;
        newOption.textContent = skill.name;
        selectElement.appendChild(newOption);
    }
}