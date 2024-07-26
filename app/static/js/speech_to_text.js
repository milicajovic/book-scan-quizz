// speech_to_text.js

document.addEventListener('DOMContentLoaded', function () {
    const resultElement = document.getElementById('result');
    const recordButton = document.getElementById('recordButton');
    const buttonText = document.getElementById('buttonText');
    const animatedSvg = recordButton.querySelector('svg');

    let recognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (recognition) {

        recognition = new recognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = 'en-US';

        recognition.onstart = () => {
            buttonText.textContent = 'Release to Stop';
            animatedSvg.style.display = 'inline-block';
            console.log('Recording started');
        };

        let finalTranscript = '';


        recognition.onresult = function (event) {
            let interimTranscript = '';
            for (let i = event.resultIndex; i < event.results.length; i++) {
                let transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalTranscript += transcript;
                } else {
                    interimTranscript += transcript;
                }
            }
            resultElement.innerHTML = finalTranscript + '<i style="color: #999;">' + interimTranscript + '</i>';
        };
        recognition.onerror = function (event) {
            console.error('Speech recognition error:', event.error);
            stopRecording();
        };

        recognition.onend = function () {
            stopRecording();
        };

        recordButton.addEventListener('mousedown', startRecording);
        recordButton.addEventListener('mouseup', stopRecording);
        recordButton.addEventListener('mouseleave', stopRecording);

        // Touch events for mobile devices
        recordButton.addEventListener('touchstart', function (e) {
            e.preventDefault(); // Prevent mousedown event on some browsers
            startRecording();
        });
        recordButton.addEventListener('touchend', stopRecording);
    } else {
        console.error('Speech recognition not supported');
        recordButton.disabled = true;
        resultElement.innerText = 'Speech recognition is not supported in this browser.';
    }

     function startRecording() {
        // Don't reset finalTranscript here
        recognition.start();
    }

    function stopRecording() {
        if (recognition) {
            recognition.stop();
            buttonText.textContent = 'Push to Answer';
            animatedSvg.style.display = 'none';
            console.log('Recording stopped');
        }
    }
});