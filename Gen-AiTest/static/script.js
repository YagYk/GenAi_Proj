const video = document.getElementById('webcam');
const captureButton = document.getElementById('capture');
const toggleCameraButton = document.getElementById('toggle-camera');
const saveImageButton = document.getElementById('save-image');
const deleteImageButton = document.getElementById('delete-image');
const capturedImage = document.getElementById('captured-image');
const chatMessages = document.getElementById('chat-messages');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-message');
const cursorDot = document.getElementById('cursor-dot');

let stream;

// Cursor dot
document.addEventListener('mousemove', (e) => {
    cursorDot.style.left = e.clientX + 'px';
    cursorDot.style.top = e.clientY + 'px';
});

// Access the webcam
async function startWebcam() {
    try {
        stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;
    } catch (error) {
        console.error('Error accessing the webcam:', error);
        alert('Unable to access the webcam. Please ensure you have given permission and that your webcam is connected.');
    }
}

// Toggle camera
toggleCameraButton.addEventListener('click', () => {
    if (video.srcObject) {
        video.srcObject.getTracks().forEach(track => track.stop());
        video.srcObject = null;
        toggleCameraButton.textContent = 'Turn On Camera';
    } else {
        startWebcam();
        toggleCameraButton.textContent = 'Turn Off Camera';
    }
});

// Call startWebcam when the page loads
document.addEventListener('DOMContentLoaded', startWebcam);

// Capture image
captureButton.addEventListener('click', () => {
    if (!video.srcObject) {
        alert('Camera is not started. Please turn on the camera.');
        return;
    }

    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);
    const imageDataUrl = canvas.toDataURL('image/jpeg');
    
    // Send the image to the server for processing
    fetch('/process_image', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ image: imageDataUrl }),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.processed_image) {
            capturedImage.src = 'data:image/jpeg;base64,' + data.processed_image;
            addMessage('AI', 'Image processed. What would you like to know about the makeup?');
        } else {
            throw new Error('Processed image data is missing');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        addMessage('System', 'An error occurred while processing the image. Please try again.');
    });
});

// Save image
saveImageButton.addEventListener('click', () => {
    if (!capturedImage.src) {
        alert('No image to save. Please capture an image first.');
        return;
    }

    fetch('/save_image', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ image: capturedImage.src }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.message);
        } else {
            throw new Error(data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to save the image. Please try again.');
    });
});

// Delete image
deleteImageButton.addEventListener('click', () => {
    if (!capturedImage.src) {
        alert('No image to delete.');
        return;
    }

    // For simplicity, we're just clearing the image on the frontend
    // In a real application, you'd also delete it from the server
    capturedImage.src = '';
    alert('Image deleted.');
});

// Send message
sendButton.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

function sendMessage() {
    const message = userInput.value.trim();
    if (message) {
        addMessage('You', message);
        // Here you would typically send the message to a backend for processing
        // For now, we'll just have a simple response
        setTimeout(() => {
            addMessage('AI', "I'm sorry, I'm a simple demo and can't actually process that request.");
        }, 1000);
        userInput.value = '';
    }
}

function addMessage(sender, message) {
    const messageElement = document.createElement('div');
    messageElement.innerHTML = `<strong>${sender}:</strong> ${message}`;
    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}
