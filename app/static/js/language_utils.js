class LanguageUtils {
    // Get the preferred language
    static getPreferredLanguage() {
        // First, try to get the language from localStorage (set by voice selection)
        const selectedLanguage = localStorage.getItem('selectedLanguageCode');
        if (selectedLanguage) {
            return selectedLanguage;
        }

        // If not set, use the browser's language
        const browserLanguage = navigator.language || navigator.userLanguage;
        return browserLanguage.split('-')[0]; // Return the primary language code
    }

    // Set the selected language
    static setSelectedLanguage(languageCode) {
        localStorage.setItem('selectedLanguageCode', languageCode);
    }
}

export default LanguageUtils;