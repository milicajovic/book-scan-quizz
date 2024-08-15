import TextToSpeechEngine from "./text_to_speech_engine.js";


class TtsStreamProcessor {
    constructor() {
        this.textToSpeech = TextToSpeechEngine.getInstance();
        this.textBuffer = '';
    }

    processStreamResponse(reader) {
        const decoder = new TextDecoder();

        const readChunk = () => {
            reader.read().then(({done, value}) => {
                if (done) {
                    this.textToSpeech.finishSpeaking();
                    return;
                }

                this.handleStreamChunk(decoder.decode(value, {stream: true}));

                readChunk();
            }).catch(error => {
                console.error('Error reading stream:', error);
            });
        };

        readChunk();
    }

    handleStreamChunk(chunk) {
        this.textBuffer += chunk;
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
}

export default TtsStreamProcessor;