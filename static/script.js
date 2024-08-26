let mediaRecorder;
let audioChunks = [];

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);

        mediaRecorder.ondataavailable = event => {
            audioChunks.push(event.data);
        };

        mediaRecorder.start();
        document.getElementById('start-recording-register').style.display = 'none';
        document.getElementById('stop-recording-register').style.display = 'inline-block';
    } catch (error) {
        console.error('Error starting recording:', error);
        document.getElementById('result').innerText = 'Error starting recording.';
    }
}

function stopRecording() {
    return new Promise((resolve) => {
        mediaRecorder.onstop = () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            resolve(audioBlob);
            audioChunks = [];
        };

        mediaRecorder.stop();
        document.getElementById('start-recording-register').style.display = 'inline-block';
        document.getElementById('stop-recording-register').style.display = 'none';
    });
}

document.getElementById('start-recording-register').onclick = startRecording;
document.getElementById('stop-recording-register').onclick = async function() {
    const audioBlob = await stopRecording();
    
    const formData = new FormData();
    formData.append('file', audioBlob, 'recording.wav');

    try {
        const response = await fetch('/register', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        document.getElementById('result').innerText = JSON.stringify(result);
    } catch (error) {
        console.error('Error during registration recording:', error);
        document.getElementById('result').innerText = 'Error during registration recording.';
    }
};

// Similar code for identification recording
document.getElementById('start-recording-identify').onclick = startRecording;
document.getElementById('stop-recording-identify').onclick = async function() {
    const audioBlob = await stopRecording();
    
    const formData = new FormData();
    formData.append('file', audioBlob, 'recording.wav');

    try {
        const response = await fetch('/identify', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        document.getElementById('result').innerText = `Speaker: ${result.speaker_name}`;
    } catch (error) {
        console.error('Error during identification recording:', error);
        document.getElementById('result').innerText = 'Error during identification recording.';
    }
};
