const socialPlatforms = {
    website: { icon: 'globe', color: 'text-secondary', label: 'Personal Website' },
    github: { icon: 'github', color: 'text-dark', label: 'GitHub' },
    linkedin: { icon: 'linkedin', color: 'text-primary', label: 'LinkedIn' },
    gitlab: { icon: 'gitlab', color: 'text-danger', label: 'GitLab' },
    stackoverflow: { icon: 'stack-overflow', color: 'text-warning', label: 'Stack Overflow' },
    medium: { icon: 'medium', color: 'text-dark', label: 'Medium' },
    devto: { icon: 'dev', color: 'text-dark', label: 'Dev.to' },
    portfolio: { icon: 'briefcase', color: 'text-info', label: 'Portfolio' },
    other: { icon: 'link-45deg', color: 'text-secondary', label: 'Other' }
};

let socialLinks = [];
let tempLinks = []; // Temporary storage for form changes

function loadSocialLinks() {
    fetch('/social-links')
        .then(response => response.json())
        .then(links => {
            socialLinks = links;
            tempLinks = [...links]; // Create a copy for form editing
            renderSocialLinksList();
        })
        .catch(error => console.error('Error loading social links:', error));
}

function renderSocialLinksList() {
    const list = document.getElementById('socialLinksList');
    list.innerHTML = '';
    
    socialLinks.forEach(link => {
        const platform = socialPlatforms[link.platform];
        const li = document.createElement('li');
        li.className = 'list-group-item d-flex justify-content-between align-items-center flex-wrap social-link-item';
        li.style.cursor = 'pointer';
        li.onclick = () => window.open(link.url, '_blank');
        li.innerHTML = `
            <h6 class="mb-0">
                <i class="bi bi-${platform.icon} ${platform.color} me-2"></i>
                ${platform.label}
            </h6>
            <span class="text-secondary social-link-name">
                ${link.display_name || link.url}
            </span>
        `;
        list.appendChild(li);
    });
}

function renderSocialLinksForm() {
    const form = document.getElementById('socialLinksForm');
    form.innerHTML = '';
    
    tempLinks.forEach((link, index) => {
        const div = document.createElement('div');
        div.className = 'mb-3 position-relative';
        div.innerHTML = `
            <div class="d-flex gap-2">
                <div class="flex-grow-1">
                    <label class="form-label">Platform</label>
                    <select class="form-select" onchange="updateTempLink(${index}, 'platform', this.value)">
                        ${Object.keys(socialPlatforms).map(platform => 
                            `<option value="${platform}" ${platform === link.platform ? 'selected' : ''}>
                                ${socialPlatforms[platform].label}
                            </option>`
                        ).join('')}
                    </select>
                </div>
                <div class="flex-grow-1">
                    <label class="form-label">URL</label>
                    <input type="url" class="form-control" value="${link.url}" 
                           onchange="updateTempLink(${index}, 'url', this.value)"
                           placeholder="https://...">
                </div>
                <div class="flex-grow-1">
                    <label class="form-label">Display Name</label>
                    <input type="text" class="form-control" value="${link.display_name || ''}" 
                           onchange="updateTempLink(${index}, 'display_name', this.value)"
                           placeholder="How it should appear">
                </div>
                <div class="d-flex align-items-end">
                    <button type="button" class="btn btn-outline-danger btn-sm mb-1" 
                            onclick="removeTempLink(${index})">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </div>
        `;
        form.appendChild(div);
    });

    const addLinkBtn = document.querySelector('#socialLinksModal .btn-outline-primary');
    if (addLinkBtn) {
        addLinkBtn.onclick = addNewLinkField;
    }
}

function addNewLinkField() {
    tempLinks.push({
        platform: 'other',
        url: '',
        display_name: '',
        isNew: true // Flag to identify new links
    });
    renderSocialLinksForm();
}

function removeTempLink(index) {
    tempLinks.splice(index, 1);
    renderSocialLinksForm();
}

function updateTempLink(index, field, value) {
    tempLinks[index][field] = value;
}

function saveSocialLinks() {
    const promises = [];

    const deletedLinks = socialLinks.filter(link => 
        !tempLinks.some(tempLink => tempLink.id === link.id)
    );
    
    deletedLinks.forEach(link => {
        promises.push(
            fetch(`/social-links/${link.id}/delete`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': CSRF_TOKEN
                }
            })
        );
    });

    // Handle updates and new links
    tempLinks.forEach(link => {
        if (link.isNew) {
            // Create new link
            promises.push(
                fetch('/social-links/add', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': CSRF_TOKEN
                    },
                    body: JSON.stringify({
                        platform: link.platform,
                        url: link.url,
                        display_name: link.display_name
                    })
                }).then(response => response.json())
            );
        } else {
            // Update existing link
            promises.push(
                fetch(`/social-links/${link.id}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': CSRF_TOKEN
                    },
                    body: JSON.stringify({
                        platform: link.platform,
                        url: link.url,
                        display_name: link.display_name
                    })
                }).then(response => response.json())
            );
        }
    });

    // Wait for all operations to complete
    Promise.all(promises)
        .then(() => {
            loadSocialLinks(); // Reload links to get updated data
            const modal = bootstrap.Modal.getInstance(document.getElementById('socialLinksModal'));
            modal.hide();
        })
        .catch(error => {
            console.error('Error saving social links:', error);
            alert('There was an error saving your changes. Please try again.');
        });
}

// Initialize social links functionality
document.addEventListener('DOMContentLoaded', function() {
    loadSocialLinks();
    // Add modal event listener
    document.getElementById('socialLinksModal').addEventListener('show.bs.modal', function () {
        tempLinks = [...socialLinks]; // Reset temp links when opening modal
        renderSocialLinksForm();
    });
}); 