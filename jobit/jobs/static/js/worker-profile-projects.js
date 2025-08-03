// Project management functionality
let projects = [];
let technologies = new Set();
let editTechnologies = new Set();
let projectToDelete = null;



// Initialize projects from Django template
function initializeProjects(projectsData) {
    projects = projectsData;
}

// Save new project
function saveProject() {
    const title = document.getElementById('projectTitle').value.trim();
    const description = document.getElementById('projectDescription').value.trim();
    const githubLink = document.getElementById('githubLink').value.trim();
    const demoLink = document.getElementById('demoLink').value.trim();
    
    if (!title || !description) {
        showToast('Please fill in all required fields', 'error');
        return;
    }
    
    const projectData = {
        title: title,
        description: description,
        technologies: Array.from(technologies),
        githubLink: githubLink || null,
        demoLink: demoLink || null
    };
    

    
    fetch('/projects/add', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': CSRF_TOKEN
        },
        body: JSON.stringify(projectData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Add new project to projects array
            projects.push(data.project);
            
            // Update the projects display
            displayProjects();
            
            // Reset form and close modal
            resetProjectForm();
            
            // Close modal
            const modalElement = document.getElementById('addProjectModal');
            if (modalElement) {
                // Try multiple approaches to close the modal
                try {
                    const bsModal = bootstrap.Modal.getInstance(modalElement);
                    if (bsModal) {
                        bsModal.hide();
                    } else {
                        // Create new instance and hide
                        const newModal = new bootstrap.Modal(modalElement);
                        newModal.hide();
                    }
                } catch (error) {
                    // Fallback: trigger the close button
                    const closeButton = modalElement.querySelector('[data-bs-dismiss="modal"]');
                    if (closeButton) {
                        closeButton.click();
                    }
                }
            }
            
            showToast('Project added successfully', 'success');
        } else {
            showToast(data.error || 'Failed to add project', 'error');
        }
    })
    .catch(error => {
        console.error('Error adding project:', error);
        showToast('An error occurred while adding the project', 'error');
    });
}

// Reset project form
function resetProjectForm() {
    document.getElementById('projectTitle').value = '';
    document.getElementById('projectDescription').value = '';
    document.getElementById('githubLink').value = '';
    document.getElementById('demoLink').value = '';
    
    // Clear technologies
    technologies.clear();
    const technologiesList = document.getElementById('technologiesList');
    if (technologiesList) {
        technologiesList.innerHTML = '';
    }
    
    // Reset character counters
    updateCharCounter('projectTitle', 'titleCharCounter', 100);
    updateCharCounter('projectDescription', 'descriptionCharCounter', 250);
}

// Display projects in the UI
function displayProjects() {
    const projectsContainer = document.getElementById('projectsList');
    if (!projectsContainer) return;
    
    projectsContainer.innerHTML = '';
    
    projects.forEach((project, index) => {
        const projectCard = document.createElement('div');
        projectCard.className = 'card mb-3 project-card';
        projectCard.innerHTML = `
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <h5 class="card-title mb-0">${project.title}</h5>
                    <div class="dropdown">
                        <button class="btn btn-link text-dark p-0" type="button" data-bs-toggle="dropdown">
                            <i class="bi bi-three-dots-vertical"></i>
                        </button>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="javascript:void(0)" onclick="editProject(${project.id})"><i class="bi bi-pencil me-2"></i>Edit</a></li>
                            <li><a class="dropdown-item text-danger" href="javascript:void(0)" onclick="deleteProject(${project.id})"><i class="bi bi-trash me-2"></i>Delete</a></li>
                        </ul>
                    </div>
                </div>
                <p class="card-text text-muted">${project.description}</p>
                <div class="mb-3">
                    ${project.technologies.map(tech => `<span class="badge bg-primary me-1">${tech}</span>`).join('')}
                </div>
                <div class="d-flex gap-2">
                    ${project.githubLink ? `<a href="${project.githubLink}" class="btn btn-outline-primary btn-sm" target="_blank"><i class="bi bi-github me-1"></i>GitHub</a>` : ''}
                    ${project.demoLink ? `<a href="${project.demoLink}" class="btn btn-outline-secondary btn-sm" target="_blank"><i class="bi bi-globe me-1"></i>Live Demo</a>` : ''}
                </div>
            </div>
        `;
        projectsContainer.appendChild(projectCard);
    });
}

// Delete project
function deleteProject(projectId) {
    projectToDelete = projectId;
    const modal = new bootstrap.Modal(document.getElementById('confirmDeleteProjectModal'));
    modal.show();
}

// Confirm delete project
function confirmDeleteProject() {
    if (!projectToDelete) return;
    
    fetch(`/projects/delete/${projectToDelete}`, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': CSRF_TOKEN
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Remove from projects array
            projects = projects.filter(p => p.id !== projectToDelete);
            
            // Update display
            displayProjects();
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('confirmDeleteProjectModal'));
            modal.hide();
            
            showToast('Project deleted successfully', 'success');
        } else {
            showToast(data.error || 'Failed to delete project', 'error');
        }
    })
    .catch(error => {
        console.error('Error deleting project:', error);
        showToast('An error occurred while deleting the project', 'error');
    })
    .finally(() => {
        projectToDelete = null;
    });
}

// Edit project
function editProject(projectId) {
    const project = projects.find(p => p.id === projectId);
    if (!project) return;
    
    // Populate edit form
    document.getElementById('editProjectTitle').value = project.title;
    document.getElementById('editProjectDescription').value = project.description;
    document.getElementById('editGithubLink').value = project.githubLink || '';
    document.getElementById('editDemoLink').value = project.demoLink || '';
    document.getElementById('editProjectId').value = project.id;
    
    // Clear and populate technologies
    editTechnologies.clear();
    document.getElementById('editTechnologiesList').innerHTML = '';
    
    project.technologies.forEach(tech => {
        editTechnologies.add(tech);
        const tag = document.createElement('span');
        tag.className = 'badge bg-primary me-2 mb-2';
        tag.innerHTML = `
            ${tech}
            <button type="button" class="btn-close btn-close-white ms-2" 
                    onclick="removeEditTechnology(this, '${tech}')" 
                    style="font-size: 0.5rem;"></button>
        `;
        document.getElementById('editTechnologiesList').appendChild(tag);
    });
    
    // Update character counters
    updateCharCounter('editProjectTitle', 'editTitleCharCounter', 100);
    updateCharCounter('editProjectDescription', 'editDescriptionCharCounter', 250);
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('editProjectModal'));
    modal.show();
}

// Update project
function updateProject() {
    const projectId = document.getElementById('editProjectId').value;
    const title = document.getElementById('editProjectTitle').value.trim();
    const description = document.getElementById('editProjectDescription').value.trim();
    const githubLink = document.getElementById('editGithubLink').value.trim();
    const demoLink = document.getElementById('editDemoLink').value.trim();
    
    if (!title || !description) {
        showToast('Please fill in all required fields', 'error');
        return;
    }
    
    const projectData = {
        title: title,
        description: description,
        technologies: Array.from(editTechnologies),
        githubLink: githubLink || null,
        demoLink: demoLink || null
    };
    
    fetch(`/projects/update/${projectId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': CSRF_TOKEN
        },
        body: JSON.stringify(projectData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update project in array
            const index = projects.findIndex(p => p.id == projectId);
            if (index !== -1) {
                projects[index] = data.project;
            }
            
            // Update display
            displayProjects();
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('editProjectModal'));
            modal.hide();
            
            showToast('Project updated successfully', 'success');
        } else {
            showToast(data.error || 'Failed to update project', 'error');
        }
    })
    .catch(error => {
        console.error('Error updating project:', error);
        showToast('An error occurred while updating the project', 'error');
    });
}

// Add technology (for new project)
function addTechnology(button) {
    const inputGroup = button.closest('.input-group');
    const input = inputGroup.querySelector('input');
    const technology = input.value.trim();
    
    if (technology) {
        // Add to technologies set
        technologies.add(technology);
        
        // Create technology tag
        const tag = document.createElement('span');
        tag.className = 'badge bg-primary me-2 mb-2';
        tag.innerHTML = `
            ${technology}
            <button type="button" class="btn-close btn-close-white ms-2" 
                    onclick="removeTechnology(this, '${technology}')" 
                    style="font-size: 0.5rem;"></button>
        `;
        
        // Add to technologies list
        const technologiesList = document.getElementById('technologiesList');
        technologiesList.appendChild(tag);
        
        // Clear input
        input.value = '';
    }
}

// Remove technology (for new project)
function removeTechnology(button, technology) {
    // Remove from technologies set
    technologies.delete(technology);
    
    // Remove tag from DOM
    button.closest('.badge').remove();
}

// Add technology (for edit project)
function addTechnologyEdit(button) {
    const inputGroup = button.closest('.input-group');
    const input = inputGroup.querySelector('input');
    const technology = input.value.trim();
    
    if (technology) {
        // Add to editTechnologies set
        editTechnologies.add(technology);
        
        // Create technology tag
        const tag = document.createElement('span');
        tag.className = 'badge bg-primary me-2 mb-2';
        tag.innerHTML = `
            ${technology}
            <button type="button" class="btn-close btn-close-white ms-2" 
                    onclick="removeEditTechnology(this, '${technology}')" 
                    style="font-size: 0.5rem;"></button>
        `;
        
        // Add to edit technologies list
        const editTechnologiesList = document.getElementById('editTechnologiesList');
        editTechnologiesList.appendChild(tag);
        
        // Clear input
        input.value = '';
    }
}

// Remove technology (for edit project)
function removeEditTechnology(button, technology) {
    // Remove from editTechnologies set
    editTechnologies.delete(technology);
    
    // Remove tag from DOM
    button.closest('.badge').remove();
}

// Update character counter
function updateCharCounter(inputId, counterId, maxLength) {
    const input = document.getElementById(inputId);
    const counter = document.getElementById(counterId);
    
    if (input && counter) {
        const remaining = maxLength - input.value.length;
        counter.textContent = `${remaining} characters remaining`;
    }
}

// Initialize character counters
document.addEventListener('DOMContentLoaded', function() {
    // Add event listeners for character counters
    const titleInput = document.getElementById('projectTitle');
    const descriptionInput = document.getElementById('projectDescription');
    const editTitleInput = document.getElementById('editProjectTitle');
    const editDescriptionInput = document.getElementById('editProjectDescription');
    
    if (titleInput) {
        titleInput.addEventListener('input', () => updateCharCounter('projectTitle', 'titleCharCounter', 100));
    }
    
    if (descriptionInput) {
        descriptionInput.addEventListener('input', () => updateCharCounter('projectDescription', 'descriptionCharCounter', 250));
    }
    
    if (editTitleInput) {
        editTitleInput.addEventListener('input', () => updateCharCounter('editProjectTitle', 'editTitleCharCounter', 100));
    }
    
    if (editDescriptionInput) {
        editDescriptionInput.addEventListener('input', () => updateCharCounter('editProjectDescription', 'editDescriptionCharCounter', 250));
    }
    
    // Add event listener for confirm delete button
    const confirmDeleteButton = document.getElementById('confirmDeleteProjectButton');
    if (confirmDeleteButton) {
        confirmDeleteButton.addEventListener('click', confirmDeleteProject);
    }
}); 