let currentSkillId = null;
let currentSkillName = null;
let currentSkillLevel = null;

function editSkill(id, level, name) {
    console.log('edit skill called for skill id: ', id);
    console.log("skill level: ", level);
    console.log("skill name: ", name);

    currentSkillId = id;
    currentSkillName = name;
    currentSkillLevel = parseInt(level);

    setInitialSkillLevel(level);
    addSkillLevelClickHandlers();

    // Add save button handler
    document.getElementById('saveSkillButton').onclick = function() {
        saveSkillLevel();
    };

    // Add remove button handler
    document.getElementById("removeSkillButton").onclick = function () {
        console.log("Trying to remove skill");
        removeSkill(id, name);
    };
}

function setInitialSkillLevel(level) {
    const skillLevels = document.querySelectorAll("#editSkillModal .progress-bar");
    skillLevels.forEach(l => l.classList.remove("active"));
    
    if (level == 1) {
        document.getElementById("beginnerEdit").classList.add("active");
    } else if (level == 2) {
        document.getElementById("intermediateEdit").classList.add("active");
    } else if (level == 3) {
        document.getElementById("advancedEdit").classList.add("active");
    }
    
    document.getElementById("skillLevelSelectEdit").value = level;
}

function addSkillLevelClickHandlers() {
    const skillLevels = document.querySelectorAll("#editSkillModal .progress-bar");
    const selectedSkillLevelInput = document.getElementById("skillLevelSelectEdit");
    
    // Remove any existing click handlers
    skillLevels.forEach(level => {
        level.removeEventListener("click", handleSkillLevelClick);
    });
    
    // Add new click handlers
    skillLevels.forEach(level => {
        level.addEventListener("click", handleSkillLevelClick);
    });
    
    function handleSkillLevelClick() {
        skillLevels.forEach(l => l.classList.remove("active"));
        this.classList.add("active");
        selectedSkillLevelInput.value = this.getAttribute("aria-valuenow");
    }
}

function saveSkillLevel() {
    const newLevel = document.getElementById("skillLevelSelectEdit").value;
    console.log('Saving skill level:', newLevel);
    console.log('Current skill level:', currentSkillLevel);
    
    if (newLevel == currentSkillLevel) {
        showToast("No changes to save", "info");
        return;
    }

    fetch('/update_skill_level', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': CSRF_TOKEN
        },
        body: JSON.stringify({
            skillId: currentSkillId,
            newLevel: newLevel
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
        currentSkillLevel = parseInt(newLevel);
        updateSkillUI(currentSkillId, newLevel);
        showToast("Skill level updated successfully", "success");
        
        // Close the modal
        let editSkillModalElement = document.getElementById("editSkillModal");
        let editSkillModal = bootstrap.Modal.getInstance(editSkillModalElement);
        editSkillModal.hide();
    })
    .catch(error => {
        console.error('ERROR:', error);
        showToast("Failed to update skill level", "error");
    });
}

function updateSkillUI(skillId, newLevel) {
    const skillItem = document.getElementById(`skillItem-${skillId}`);
    const progressBar = skillItem.querySelector('.progress-bar');
    const editButton = skillItem.querySelector('.bi-pencil');
    
    // Update progress bar class and width based on new level
    if (newLevel == 1) {
        progressBar.className = 'progress-bar bg-success';
        progressBar.style.width = '33%';
    } else if (newLevel == 2) {
        progressBar.className = 'progress-bar bg-warning';
        progressBar.style.width = '66%';
    } else if (newLevel == 3) {
        progressBar.className = 'progress-bar bg-danger';
        progressBar.style.width = '100%';
    }

    // Update the edit button's onclick attribute with the new level
    editButton.setAttribute('onclick', `editSkill('${skillId}', '${newLevel}', '${currentSkillName}')`);
}

function removeSkill(id, name) {
    fetch('/remove-skill', {
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
        let skillItemId = "skillItem-".concat(id.toString());
        let skillItem = document.getElementById(skillItemId);
        skillItem.remove();
        showToast("Skill removed successfully: ".concat(name), "success");
    })
    .catch(error => {
        console.error('ERROR:', error);
        showToast("Failed to remove skill: ".concat(name), "error");
    });
}
