const MAX_CHARS = 250;

function updateCharCounter() {
    const textarea = document.getElementById('aboutMeText');
    const counter = document.getElementById('charCounter');
    const currentLength = textarea.value.length;
    counter.textContent = `${currentLength}/250`;
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
    // Remove input event listener
    textarea.removeEventListener('input', updateCharCounter);
}

function saveAboutMe() {
    const newAboutMe = document.getElementById('aboutMeText').value.trim();
    const content = document.getElementById('aboutMeContent');
    const edit = document.getElementById('aboutMeEdit');
    const textarea = document.getElementById('aboutMeText');
    
    fetch('/update_about_me', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': CSRF_TOKEN
        },
        body: JSON.stringify({
            aboutMe: newAboutMe
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
        content.textContent = newAboutMe;
        content.style.display = 'block';
        edit.style.display = 'none';
        // Remove input event listener
        textarea.removeEventListener('input', updateCharCounter);
        showToast("About Me updated successfully", "success");
    })
    .catch(error => {
        console.error('ERROR:', error);
        showToast("Failed to update About Me", "error");
    });
}

document.addEventListener('DOMContentLoaded', function() {
}); 