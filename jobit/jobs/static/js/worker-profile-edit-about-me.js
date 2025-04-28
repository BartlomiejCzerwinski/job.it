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
    } else {
        // Switch to view mode
        content.style.display = 'block';
        edit.style.display = 'none';
    }
}

function cancelAboutMeEdit() {
    const content = document.getElementById('aboutMeContent');
    const edit = document.getElementById('aboutMeEdit');
    
    content.style.display = 'block';
    edit.style.display = 'none';
}

function saveAboutMe() {
    const newAboutMe = document.getElementById('aboutMeText').value.trim();
    const content = document.getElementById('aboutMeContent');
    const edit = document.getElementById('aboutMeEdit');
    
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
        showToast("About Me updated successfully", "success");
    })
    .catch(error => {
        console.error('ERROR:', error);
        showToast("Failed to update About Me", "error");
    });
}

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('saveAboutMeButton').addEventListener('click', function() {
        const newAboutMe = document.getElementById('aboutMeText').value.trim();
        
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
            document.getElementById('aboutMeContent').textContent = newAboutMe;
            showToast("About Me updated successfully", "success");
            
            const editAboutMeModal = bootstrap.Modal.getInstance(document.getElementById('editAboutMeModal'));
            editAboutMeModal.hide();
        })
        .catch(error => {
            console.error('ERROR:', error);
            showToast("Failed to update About Me", "error");
        });
    });
}); 