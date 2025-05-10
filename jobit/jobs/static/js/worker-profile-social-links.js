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

function loadSocialLinks() {
    fetch('/social-links')
        .then(response => response.json())
        .then(links => {
            socialLinks = links;
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
    
    socialLinks.forEach((link, index) => {
        const div = document.createElement('div');
        div.className = 'mb-3 position-relative';
        div.innerHTML = `
            <div class="d-flex gap-2">
                <div class="flex-grow-1">
                    <label class="form-label">Platform</label>
                    <select class="form-select" onchange="updatePlatform(${index}, this.value)">
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
                           onchange="updateValue(${index}, this.value)"
                           placeholder="https://...">
                </div>
                <div class="flex-grow-1">
                    <label class="form-label">Display Name</label>
                    <input type="text" class="form-control" value="${link.display_name || ''}" 
                           onchange="updateDisplayName(${index}, this.value)"
                           placeholder="How it should appear">
                </div>
                <div class="d-flex align-items-end">
                    <button type="button" class="btn btn-outline-danger btn-sm mb-1" 
                            onclick="removeLink(${index})">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </div>
        `;
        form.appendChild(div);
    });
}

function addNewLinkField() {
    const newLink = { platform: 'other', url: '', display_name: '' };
    fetch('/social-links/add', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': CSRF_TOKEN
        },
        body: JSON.stringify(newLink)
    })
    .then(response => response.json())
    .then(link => {
        socialLinks.push(link);
        renderSocialLinksForm();
    })
    .catch(error => console.error('Error adding social link:', error));
}

function removeLink(index) {
    const link = socialLinks[index];
    if (!link || !link.id) {
        console.error('Invalid link or missing ID');
        return;
    }

    fetch(`/social-links/${link.id}/delete`, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': CSRF_TOKEN
        }
    })
    .then(response => {
        if (response.ok) {
            socialLinks.splice(index, 1);
            renderSocialLinksForm();
        } else {
            throw new Error('Failed to delete social link');
        }
    })
    .catch(error => console.error('Error deleting social link:', error));
}

function updatePlatform(index, platform) {
    const link = socialLinks[index];
    if (!link || !link.id) {
        console.error('Invalid link or missing ID');
        return;
    }

    const formData = {
        platform: platform,
        url: link.url,
        display_name: link.display_name
    };
    
    fetch(`/social-links/${link.id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': CSRF_TOKEN
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(updatedLink => {
        socialLinks[index] = updatedLink;
        renderSocialLinksForm();
    })
    .catch(error => console.error('Error updating platform:', error));
}

function updateValue(index, value) {
    const link = socialLinks[index];
    if (!link || !link.id) {
        console.error('Invalid link or missing ID');
        return;
    }

    const formData = {
        platform: link.platform,
        url: value,
        display_name: link.display_name
    };
    
    fetch(`/social-links/${link.id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': CSRF_TOKEN
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(updatedLink => {
        socialLinks[index] = updatedLink;
        renderSocialLinksForm();
    })
    .catch(error => console.error('Error updating URL:', error));
}

function updateDisplayName(index, name) {
    const link = socialLinks[index];
    if (!link || !link.id) {
        console.error('Invalid link or missing ID');
        return;
    }

    const formData = {
        platform: link.platform,
        url: link.url,
        display_name: name
    };
    
    fetch(`/social-links/${link.id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': CSRF_TOKEN
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(updatedLink => {
        socialLinks[index] = updatedLink;
        renderSocialLinksForm();
    })
    .catch(error => console.error('Error updating display name:', error));
}

function saveSocialLinks() {
    renderSocialLinksList();
    const modal = bootstrap.Modal.getInstance(document.getElementById('socialLinksModal'));
    modal.hide();
}

document.addEventListener('DOMContentLoaded', function() {
    loadSocialLinks();
    
    document.getElementById('socialLinksModal').addEventListener('show.bs.modal', function () {
        renderSocialLinksForm();
    });
}); 