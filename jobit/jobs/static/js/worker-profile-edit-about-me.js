const ABOUT_ME_URL = "http://127.0.0.1:8000/update_about_me";

function updateCharCounter() {
    const textarea = document.getElementById('aboutMeText');
    const counter = document.getElementById('charCounter');
    const remaining = 250 - textarea.value.length;
    counter.textContent = `${remaining} characters remaining`;
    
    if (remaining < 0) {
        counter.classList.add('text-danger');
    } else {
        counter.classList.remove('text-danger');
    }
}

function toggleAboutMeEdit() {
    const content = document.getElementById('aboutMeContent');
    const edit = document.getElementById('aboutMeEdit');
    const textarea = document.getElementById('aboutMeText');
    
    if (content.style.display !== 'none') {
        // Switch to edit mode
        content.style.display = 'none';
        edit.style.display = 'block';
        textarea.value = content.textContent.trim();
        textarea.focus();
        // Initialize counter with current text length
        updateCharCounter();
        // Add input event listener for real-time updates
        textarea.addEventListener('input', updateCharCounter);
    } else {
        // Switch to view mode
        content.style.display = 'block';
        edit.style.display = 'none';
        // Remove input event listener
        textarea.removeEventListener('input', updateCharCounter);
    }
}

function cancelAboutMeEdit() {
    const content = document.getElementById('aboutMeContent');
    const edit = document.getElementById('aboutMeEdit');
    const textarea = document.getElementById('aboutMeText');
    
    content.style.display = 'block';
    edit.style.display = 'none';
    textarea.removeEventListener('input', updateCharCounter);
}

function saveAboutMe() {
    const textarea = document.getElementById('aboutMeText');
    const content = document.getElementById('aboutMeContent');
    const edit = document.getElementById('aboutMeEdit');
    
    if (textarea.value.length > 250) {
        showToast('About Me text cannot exceed 250 characters', 'danger');
        return;
    }
    
    fetch(ABOUT_ME_URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            aboutMe: textarea.value
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showToast(data.error, 'danger');
        } else {
            content.textContent = textarea.value || 'No information provided yet.';
            content.style.display = 'block';
            edit.style.display = 'none';
            textarea.removeEventListener('input', updateCharCounter);
            showToast('About Me updated successfully', 'success');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('An error occurred while updating About Me', 'danger');
    });
}

function showToast(message, type = 'success') {
    const toastElement = document.getElementById('customToast');
    const toastMessage = document.getElementById('toastMessage');

    toastMessage.textContent = message;
    toastElement.classList.remove('text-bg-primary', 'text-bg-success', 'text-bg-danger');

    if (type === 'success') {
        toastElement.classList.add('text-bg-success');
    } else if (type === 'danger') {
        toastElement.classList.add('text-bg-danger');
    } else {
        toastElement.classList.add('text-bg-primary');
    }

    const toast = new bootstrap.Toast(toastElement);
    toast.show();
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener('DOMContentLoaded', function() {
    const textarea = document.getElementById('aboutMeText');
    if (textarea) {
        textarea.addEventListener('input', updateCharCounter);
    }
}); 