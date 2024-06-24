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
    })
    .catch(error => {
        console.error('Error:', error);
    });
});

document.getElementById('questionForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const question = document.getElementById('ques1').value;

    fetch('/ask', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({question: question})
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('ans1').value = data.answer;
    })
    .catch(error => {
        console.error('Error:', error);
    });
});