// app/static/js/language_preference_sender.js

class LanguagePreferenceSender {
    static sessionId = null;

    static init() {
        const sessionIdElement = document.getElementById('session-id');
        if (sessionIdElement) {
            this.sessionId = sessionIdElement.value;
        } else {
            console.error('LanguagePreferenceSender: session-id element not found. Language preferences cannot be sent.');
        }
    }

    static sendLanguagePreference(languageCode) {
        if (!this.sessionId) {
            console.error('LanguagePreferenceSender: Cannot send language preference. Session ID is not set.');
            return;
        }

        fetch(`/quiz-session/set-language`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: this.sessionId,
                language: languageCode
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('Language preference set successfully');
            } else {
                console.error('Failed to set language preference:', data.error);
            }
        })
        .catch(error => {
            console.error('Error sending language preference:', error);
        });
    }
}

// Initialize the LanguagePreferenceSender when the script loads
LanguagePreferenceSender.init();

export default LanguagePreferenceSender;