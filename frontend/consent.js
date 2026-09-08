(function () {
    const CONSENT_KEY = 'toptop_consent';
    const banner = document.getElementById('cookieBanner');
    const acceptButton = document.getElementById('cookieAccept');
    const declineButton = document.getElementById('cookieDecline');

    function loadScript(src, attrs) {
        const script = document.createElement('script');
        script.src = src;
        script.async = true;
        Object.entries(attrs || {}).forEach(([key, value]) => script.setAttribute(key, value));
        document.head.appendChild(script);
        return script;
    }

    function enableAnalytics() {
        if (!window.TOPTOP_GA_ID) return;
        window.dataLayer = window.dataLayer || [];
        window.gtag = function gtag() {
            window.dataLayer.push(arguments);
        };
        loadScript(`https://www.googletagmanager.com/gtag/js?id=${window.TOPTOP_GA_ID}`);
        window.gtag('js', new Date());
        window.gtag('config', window.TOPTOP_GA_ID, { anonymize_ip: true });
    }

    function enableAds() {
        if (!window.TOPTOP_ADSENSE_ID) return;
        loadScript(
            `https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=${window.TOPTOP_ADSENSE_ID}`,
            { crossorigin: 'anonymous' }
        );

        document.querySelectorAll('.ad-slot').forEach((slot) => {
            slot.hidden = false;
            slot.textContent = '';
            const ins = document.createElement('ins');
            ins.className = 'adsbygoogle';
            ins.style.display = 'block';
            ins.setAttribute('data-ad-client', window.TOPTOP_ADSENSE_ID);
            ins.setAttribute('data-ad-format', 'auto');
            ins.setAttribute('data-full-width-responsive', 'true');
            slot.appendChild(ins);
            window.adsbygoogle = window.adsbygoogle || [];
            window.adsbygoogle.push({});
        });
    }

    function grantConsent() {
        enableAnalytics();
        enableAds();
    }

    const storedConsent = localStorage.getItem(CONSENT_KEY);

    if (storedConsent === 'accepted') {
        grantConsent();
    } else if (!storedConsent && banner) {
        banner.hidden = false;
    }

    if (acceptButton) {
        acceptButton.addEventListener('click', () => {
            localStorage.setItem(CONSENT_KEY, 'accepted');
            banner.hidden = true;
            grantConsent();
        });
    }

    if (declineButton) {
        declineButton.addEventListener('click', () => {
            localStorage.setItem(CONSENT_KEY, 'declined');
            banner.hidden = true;
        });
    }
})();
