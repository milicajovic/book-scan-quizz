import TextToSpeechEngine from "./text_to_speech_engine.js";
import quizSessionInstance from './quiz_session.js';


class TtsStreamProcessor {
    constructor() {
        this.textToSpeech = TextToSpeechEngine.getInstance();
        this.textBuffer = '';
        this.processingFeedback = document.getElementById('processingFeedback');
        this.resultText = document.getElementById('resultText');
        this.recordButton = document.getElementById('recordButton');
    }

    processStreamResponse(reader) {
        const decoder = new TextDecoder();

        const readChunk = () => {
            reader.read().then(({done, value}) => {
                if (done) {
                    this.processingFeedback.style.display = 'none';
                    this.recordButton.disabled = false;
                    this.showNextQuestionButton();
                    this.textToSpeech.finishSpeaking();
                    return;
                }

                this.handleStreamChunk(decoder.decode(value, {stream: true}));

                readChunk();
            }).catch(error => {
                console.error('Error reading stream:', error);
                this.processingFeedback.style.display = 'none';
                this.resultText.textContent += `\nError reading stream: ${error.message}`;
                this.recordButton.disabled = false;
            });
        };

        readChunk();
    }

    handleStreamChunk(chunk) {
        this.textBuffer += chunk;
        this.resultText.textContent += chunk;
        this.processSentences();
    }

    processSentences() {
        let sentenceEnd = this.textBuffer.search(/[.!?]\s/);
        while (sentenceEnd !== -1) {
            const sentence = this.textBuffer.slice(0, sentenceEnd + 1);
            this.textToSpeech.addToSpeechQueue(sentence.trim());
            this.textBuffer = this.textBuffer.slice(sentenceEnd + 1);
            sentenceEnd = this.textBuffer.search(/[.!?]\s/);
        }
    }

    showNextQuestionButton() {
        quizSessionInstance.showActionButtons();
    }
}

export default TtsStreamProcessor;