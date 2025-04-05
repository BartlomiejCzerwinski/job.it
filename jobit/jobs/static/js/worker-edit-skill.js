function editSkill(id, level, name) {
    console.log('edit skill called for skill id: ', id);
    console.log("skill level: ", level);
    let removeSkillButton = document.getElementById("removeSkillButton");

    removeSkillButton.onclick = function () {
        console.log("Trying to remove skill");
        removeSkill(id, name);
    };
}

function removeSkill (id, name) {
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