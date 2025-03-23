let SKILLS_URL = "http://127.0.0.1:8000/get_skills";
let SKILLS_IN_LISTING = [];

document.addEventListener("DOMContentLoaded", function () {
    jobLocationSearchLogic();
    addSkillModalLogic();
    modalVisibilityLogic();
    addSkillFromModalToJobListingLogic();
    beforeSendListingLogic();
});

function fetchSkills(endpointUrl) {
    return fetch(endpointUrl)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status} - ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            return data;
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

    hideErrorInModal('skillNameFeedback');
    hideErrorInModal('skillLevelFeedback');
    hideErrorInModal('skillExistsFeedback');
}

function showErrorInModal(fieldId) {
    let errorMessage = document.getElementById(fieldId);
    errorMessage.style.display = 'block';
}

function hideErrorInModal(fieldId) {
    let errorMessage = document.getElementById(fieldId);
    errorMessage.style.display = 'none';
}


function loadSkillsListInModal(skills) {
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

function addSkillToJobListing(skill) {
    for (let i = 0; i < SKILLS_IN_LISTING.length; i++) {
        if (skill.id == SKILLS_IN_LISTING[i].id && skill.name == SKILLS_IN_LISTING[i].name)
            return false // If skill is already present in Job listing
    }
    SKILLS_IN_LISTING.push(skill);
    addSkillItem(skill);
    return true; // If skill is not present in job listing, it will be successfully added
}

function removeSkillFromJobListing(skillId) {
    for (let i = 0; i < SKILLS_IN_LISTING.length; i++) {
        if (skillId == SKILLS_IN_LISTING[i].id) {
            SKILLS_IN_LISTING.splice(i, 1);
            return true; // Success
        }
    }
    return false; // Failed
}

function generateSkillHTML(skill) {
    let progressBarClass = "bg-danger";
    let progressWidth = "100%";
    let progressValue = 100;

    if (skill.level == 1) {
        progressBarClass = "bg-success";
        progressWidth = "33%";
        progressValue = 33;
    } else if (skill.level == 2) {
        progressBarClass = "bg-warning";
        progressWidth = "66%";
        progressValue = 66;
    }

    return `
        <div id="skillItem-${skill.id}">
            <div class="d-flex align-items-center">
                <small class="w-100 text-truncate">${skill.name}</small>
                <i class="bi bi-x-lg ms-auto" style="font-size: 1rem; color: black; cursor: pointer;"
                   onclick="removeSkillListItem(${skill.id})"></i>
            </div>
            <div class="progress mb-3" style="height: 5px;">
                <div class="progress-bar ${progressBarClass}" role="progressbar"
                     style="width: ${progressWidth};" aria-valuenow="${progressValue}"
                     aria-valuemin="0" aria-valuemax="100"></div>
            </div>
        </div>
    `;
}

function addSkillItem(skill) {
    let skillsList = document.getElementById("skillsList");
    let skillHTML = generateSkillHTML(skill);
    skillsList.innerHTML += skillHTML;
}

function removeSkillListItem(skillId) {
    let skillItem = document.getElementById("skillItem-".concat(skillId));
    skillItem.innerHTML = '';
    removeSkillFromJobListing(skillId);
}

// Main logic ****************************************************************************

function addSkillModalLogic() {
    const searchInput = document.getElementById("searchSkillInput");
    const skillSelect = document.getElementById("skillNameSelect");
    let isOptionSelected = false;

    searchInput.addEventListener("focus", () => {
        skillSelect.style.display = "block";
    });

    searchInput.addEventListener("input", function () {
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

    document.addEventListener("click", function (event) {
        if (!searchInput.contains(event.target) && !skillSelect.contains(event.target)) {
            if (!isOptionSelected) {
                searchInput.value = "";
            }
            skillSelect.style.display = "none";
        }
    });

    skillSelect.addEventListener("change", function () {
        searchInput.value = this.options[this.selectedIndex].text;
        isOptionSelected = true;
        skillSelect.style.display = "none";
    });

    const skillLevels = document.querySelectorAll(".progress-bar");
    const selectedSkillLevelInput = document.getElementById("skillLevelSelect");
    selectedSkillLevelInput.value = 10;

    skillLevels.forEach(level => {
        level.addEventListener("click", function () {
            skillLevels.forEach(l => l.classList.remove("active"));
            this.classList.add("active");
            selectedSkillLevelInput.value = this.getAttribute("aria-valuenow");

        });
    });
}

function jobLocationSearchLogic() {
    const locationInput = document.getElementById("id_job_location");
    const suggestionsDiv = document.getElementById("locationSuggestions");
    locationInput.addEventListener("input", function () {
        const query = locationInput.value;
        if (query.length < 3) {
            suggestionsDiv.innerHTML = "";
            return;
        }

        fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${query}`)
            .then(response => response.json())
            .then(data => {
                suggestionsDiv.innerHTML = "";
                data.forEach(location => {
                    const item = document.createElement("div");
                    item.classList.add("list-group-item", "list-group-item-action");
                    item.textContent = location.display_name;
                    item.addEventListener("click", function () {
                        locationInput.value = location.display_name;
                        suggestionsDiv.innerHTML = "";
                    });
                    suggestionsDiv.appendChild(item);
                });
            });
    });

    document.addEventListener("click", function (event) {
        if (!suggestionsDiv.contains(event.target)) {
            suggestionsDiv.innerHTML = "";
        }
    });
}

function modalVisibilityLogic() {
    let skillModal = document.getElementById("addSkillModal");

    skillModal.addEventListener("shown.bs.modal", function () {
        console.log("Modal opened.");
        fetchSkills(SKILLS_URL)
            .then(skills => {
                loadSkillsListInModal(skills);
            })
            .catch(error => console.error("Error while loading skills:", error));
    });

    skillModal.addEventListener("hidden.bs.modal", function () {
        console.log("Modal closed.");
        resetAddSkillModal();
    });
}

function addSkillFromModalToJobListingLogic() {
    document.getElementById('addSkillButton').addEventListener('click', function () {
        const skillName = document.getElementById('searchSkillInput').value.trim();
        const skillLevel = document.getElementById('skillLevelSelect').value;

        let isValid = true;

        if (!skillName) {
            showErrorInModal('skillNameFeedback')
            isValid = false;
        } else {
            hideErrorInModal('skillNameFeedback')
        }

        if (skillLevel != 1 && skillLevel != 2 && skillLevel != 3) {
            showErrorInModal('skillLevelFeedback')
            isValid = false;
        } else {
            hideErrorInModal('skillLevelFeedback')
        }

        if (isValid) {
            let skillId = getSkillId(skillName);
            let skill = {"id": skillId, "name": skillName, "level": skillLevel};
            if (addSkillToJobListing(skill)) {
                resetAddSkillModal();
                let addSkillModalElement = document.getElementById("addSkillModal");
                let addSkillModal = bootstrap.Modal.getInstance(addSkillModalElement);
                addSkillModal.hide();
                console.log(`Added skill: ${skillName} - Level: ${skillLevel}`);
            } else {
                showErrorInModal('skillExistsFeedback');
                console.log(`Cannot add skill: ${skillName} - Level: ${skillLevel}`);
            }
        } else {
            hideErrorInModal('skillExistsFeedback');
            console.log('Cannot add skill')
        }
    });
}

function beforeSendListingLogic() {
    document.querySelector("form").addEventListener("submit", function () {
        let skillsDataInput = document.getElementById("skillsListForListing");
        skillsDataInput.value = JSON.stringify(SKILLS_IN_LISTING);
    });
}