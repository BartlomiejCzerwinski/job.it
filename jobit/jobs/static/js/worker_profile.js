let SKILLS_URL = "http://127.0.0.1:8000/job.it/get_skills";

document.addEventListener("DOMContentLoaded", function() {
    const searchInput = document.getElementById("searchSkillInput");
    const skillSelect = document.getElementById("skillNameSelect");
    let isOptionSelected = false;

    searchInput.addEventListener("focus", () => {
        skillSelect.style.display = "block";
    });

    searchInput.addEventListener("input", function() {
        const filter = this.value.toLowerCase();
        const options = skillSelect.querySelectorAll("option");

        isOptionSelected = false;
        options.forEach(option => {
            if (option.textContent.toLowerCase().includes(filter)) {
                option.style.display = "";
            } else {
                option.style.display = "none";
            }
        });
    });

    document.addEventListener("click", function(event) {
        if (!searchInput.contains(event.target) && !skillSelect.contains(event.target)) {
            if (!isOptionSelected) {
                searchInput.value = "";
            }
            skillSelect.style.display = "none";
        }
    });

    skillSelect.addEventListener("change", function() {
        searchInput.value = this.options[this.selectedIndex].text;
        isOptionSelected = true;
        skillSelect.style.display = "none";
    });

    const skillLevels = document.querySelectorAll(".progress-bar");
    const selectedSkillLevelInput = document.getElementById("skillLevelSelect");
    selectedSkillLevelInput.value = 10;

    skillLevels.forEach(level => {
        level.addEventListener("click", function() {
            skillLevels.forEach(l => l.classList.remove("active"));
            this.classList.add("active");
            selectedSkillLevelInput.value = this.getAttribute("aria-valuenow");

        });
    });
});

document.getElementById('addSkillButton').addEventListener('click', function() {
    const skillName = document.getElementById('searchSkillInput').value.trim();
    const skillLevel = document.getElementById('skillLevelSelect').value;

    let isValid = true;

    if (!skillName) {
        showError('skillNameFeedback')
        isValid = false;
    } else {
        hideError('skillNameFeedback')
    }

    if (skillLevel != 1 && skillLevel != 2 && skillLevel != 3) {
        showError('skillLevelFeedback')
        isValid = false;
    } else {
        hideError('skillLevelFeedback')
    }

    if (isValid) {
        console.log(`Trying to add skill: ${skillName} - Level: ${skillLevel}`);
        let skillId = getSkillId(skillName);
        addSkillRequest(skillId, skillLevel);
    } else {
        console.log('Cannot add skill')
    }
});

function showError(fieldId) {
    let errorMessage = document.getElementById(fieldId);
    errorMessage.style.display = 'block';
}

function hideError(fieldId) {
    let errorMessage = document.getElementById(fieldId);
    errorMessage.style.display = 'none';
}

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

function getSkillId(skillName) {
    let selectElement = document.getElementById('skillNameSelect');
    let skillsArray = selectElement.children;
    for (skillObject of skillsArray) {
        if (skillObject.textContent == skillName) {
            return skillObject.value;
        }
    }
}

function addSkillRequest(skillId, skillLevel) {
    fetch('/job.it/add_skill', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': CSRF_TOKEN
        },
        body: JSON.stringify({
            skillId: skillId,
            skillLevel: skillLevel
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log('Success:', data);
        hideModal();
        showToast("Skill added successfully", "success");
        resetAddSkillModal()
    })
    .catch(error => {
        console.error('ERROR:', error);
        hideModal();
        showToast("Failed to add skill", "error");
        resetAddSkillModal()
    });
}

function hideModal() {
    let addSkillModalElement = document.getElementById("addSkillModal");
    let addSkillModal = bootstrap.Modal.getInstance(addSkillModalElement);
    addSkillModal.hide();
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

function showToast(message, type) {
    const toastElement = document.getElementById("customToast");
    const toastMessage = document.getElementById("toastMessage");

    toastMessage.innerText = message;

    toastElement.classList.remove("text-bg-primary", "text-bg-success", "text-bg-danger");

    if (type === "success") {
        toastElement.classList.add("text-bg-success");
    } else if (type === "error") {
        toastElement.classList.add("text-bg-danger");
    } else {
        toastElement.classList.add("text-bg-primary");
    }

    const toast = new bootstrap.Toast(toastElement);
    toast.show();
}

window.editSkill = function (id, level, name) {
    console.log('edit skill called', id);
    console.log("skill level: ", level);
    let removeSkillButton = document.getElementById("removeSkillButton");
    console.log(removeSkillButton);
    removeSkillButton.addEventListener("click", () => {
        console.log("listener is working");
       removeSkill(id, name);
    });
}

window.removeSkill  = function (id, name) {
    fetch('/job.it/remove-skill', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': CSRF_TOKEN
        },
        body: JSON.stringify({
            id: id
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log('Success:', data);
        showToast("Skill removed successfully: ".concat(name), "success");
    })
    .catch(error => {
        console.error('ERROR:', error);
        showToast("Failed to remove skill: ".concat(name), "error");
    });
}