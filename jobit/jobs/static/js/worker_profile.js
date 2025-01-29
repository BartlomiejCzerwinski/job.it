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
        console.log(`Skill Added: ${skillName} - Level: ${skillLevel}`);
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

function addSkillRequest(skillId, skillLevel) {

}