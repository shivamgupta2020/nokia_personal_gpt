document.getElementById('fileUploadForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const formData = new FormData();
    formData.append('file1', document.getElementById('file1').files[0]);

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        loadFileList(); // Refresh the file list after uploading a new file
    })
    .catch(error => {
        console.error('Error:', error);
    });
});

document.getElementById('questionForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const question = document.getElementById('ques1').value;
    const selectedFile = document.getElementById('fileSelect').value;

    if (!selectedFile) {
        alert('Please select a file first.');
        return;
    }

    fetch('/ask', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: question, filename: selectedFile })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('ans1').value = data.answer;
    })
    .catch(error => {
        console.error('Error:', error);
    });
});

function loadFileList() {
    fetch('/files')
    .then(response => response.json())
    .then(data => {
        const fileSelect = document.getElementById('fileSelect');
        fileSelect.innerHTML = '<option value="">Select a file</option>'; // Clear existing options
        data.forEach(file => {
            const option = document.createElement('option');
            option.value = file.filename;
            option.textContent = file.filename;
            fileSelect.appendChild(option);
        });
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// Load the file list when the page loads
document.addEventListener('DOMContentLoaded', loadFileList);