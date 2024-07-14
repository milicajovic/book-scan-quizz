// Global variables
let mediaRecorder;
let audioChunks = [];
let isRecording = false;

function initAudioRecording(submitUrl, questionId, sessionId) {
    const recordButton = document.getElementById('recordButton');
    const recordingFeedback = document.getElementById('recordingFeedback');
    const recordingDuration = document.getElementById('recordingDuration');
    const resultText = document.getElementById('resultText');
    const processingFeedback = document.getElementById('processingFeedback');
    const audioVisualization = document.getElementById('audioVisualization');
    const audioMeter = document.getElementById('audioMeter');

    let startTime;
    let durationInterval;

    recordButton.addEventListener('mousedown', startRecording);
    recordButton.addEventListener('mouseup', stopRecording);
    recordButton.addEventListener('mouseleave', stopRecording);

    function startRecording() {
        console.log("Start recording called");
        if (isRecording) {
            console.log("Already recording, ignoring start request");
            return;
        }
        isRecording = true;
        audioChunks = [];
        navigator.mediaDevices.getUserMedia({audio: true})
            .then(stream => {
                mediaRecorder = new MediaRecorder(stream);
                mediaRecorder.start();
                startTime = Date.now();
                updateUI(true);

                mediaRecorder.addEventListener("dataavailable", event => {
                    audioChunks.push(event.data);
                });

                mediaRecorder.addEventListener("stop", () => {
                    console.log("MediaRecorder stopped");
                    const audioBlob = new Blob(audioChunks, {type: 'audio/wav'});
                    console.log(`Audio blob created, size: ${audioBlob.size} bytes`);
                    sendAudioToServer(audioBlob);
                });
            })
            .catch(error => {
                console.error("Error accessing microphone:", error);
                isRecording = false;
                alert('Error accessing microphone. Please ensure you have given permission to use the microphone.');
            });
    }

    function stopRecording() {
        console.log("Stop recording called");
        if (!isRecording) {
            console.log("Not recording, ignoring stop request");
            return;
        }
        isRecording = false;
        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
            updateUI(false);
        }
    }

    function updateUI(isRecording) {
        recordButton.classList.toggle('btn-danger', isRecording);
        recordButton.classList.toggle('btn-success', !isRecording);
        recordButton.textContent = isRecording ? 'Recording...' : 'Record';
        recordingFeedback.style.display = isRecording ? 'block' : 'none';

        if (isRecording) {
            durationInterval = setInterval(updateDuration, 1000);
        } else {
            clearInterval(durationInterval);
            recordingDuration.textContent = '0';
        }
    }

    function updateDuration() {
        const duration = Math.floor((Date.now() - startTime) / 1000);
        recordingDuration.textContent = duration;
    }

    /**
     * Sends the recorded audio to the server and processes the streaming response.
     * @param {Blob} audioBlob - The recorded audio as a Blob.
     */
    function sendAudioToServer(audioBlob) {
        console.log(`Preparing to send audio to server. Blob size: ${audioBlob.size} bytes`);

        const formData = new FormData();
        formData.append("audio", audioBlob, "recording.wav");
        formData.append("question_id", questionId);
        formData.append("session_id", sessionId);

        console.log("FormData created, sending request to server");
        resultText.textContent = '';
        processingFeedback.style.display = 'block';
        recordButton.disabled = true;

        fetch(submitUrl, {
            method: 'POST',
            body: formData
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.body.getReader();
            })
            .then(reader => processStreamResponse(reader))
            .catch(error => {
                console.error('Error:', error);
                processingFeedback.style.display = 'none';
                resultText.textContent = 'Error: ' + error.message;
                resultText.style.color = 'red';
                recordButton.disabled = false;
            });
    }

    /**
     * Processes the streaming response from the server.
     * @param {ReadableStreamDefaultReader} reader - The reader for the response body stream.
     */
    function processStreamResponse(reader) {
        let accumulatedText = '';
        const decoder = new TextDecoder();

        function readChunk() {
            reader.read().then(({done, value}) => {
                if (done) {
                    console.log('Stream complete');
                    processingFeedback.style.display = 'none';
                    recordButton.disabled = false;
                    TextToSpeech.handleStreamEnd();
                    return;
                }

                const chunk = decoder.decode(value, {stream: true});
                accumulatedText += chunk;

                // Update UI
                resultText.textContent += chunk;

                // Process accumulated text for complete sentences
                const sentences = accumulatedText.match(/[^.!?]+[.!?]+/g) || [];
                sentences.forEach(sentence => {
                    TextToSpeech.speak(sentence.trim());
                });

                // Keep any remaining text that doesn't end with sentence-ending punctuation
                accumulatedText = accumulatedText.replace(/^.*[.!?]+\s*/g, '');

                // Continue reading
                readChunk();
            }).catch(error => {
                console.error('Error reading stream:', error);
                processingFeedback.style.display = 'none';
                resultText.textContent += '\nError reading stream: ' + error.message;
                recordButton.disabled = false;
            });
        }

        readChunk();
    }
}

// The DOMContentLoaded event listener has been moved to the HTML template