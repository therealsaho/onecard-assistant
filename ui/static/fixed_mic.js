// fixed_mic.js - helper to autofocus mic button when needed
window.onecardFocusMic = (shouldFocus) => {
    try {
        const btn = document.querySelector('.onecard-fixed-mic button');
        if (!btn) return;
        if (shouldFocus) btn.focus();
        else btn.blur();
    } catch (e) {
        // ignore
    }
};
