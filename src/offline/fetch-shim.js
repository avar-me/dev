// Перехватывает fetch() локальными данными из offline-data.js, чтобы сайт
// работал при открытии index.html/phrases.html напрямую через file:// —
// без запуска HTTP-сервера. Подключается в package-offline.sh только в
// офлайн-архив, перед app.js/phrases.js; на dev.avar.me не используется.
(function () {
    if (typeof window.__OFFLINE_DATA__ !== 'object') return;

    var DATA = window.__OFFLINE_DATA__;
    var originalFetch = window.fetch ? window.fetch.bind(window) : null;

    function normalize(url) {
        return String(url).split('?')[0].replace(/^\.?\//, '');
    }

    window.fetch = function (input, init) {
        var url = typeof input === 'string' ? input : (input && input.url) || '';
        var key = normalize(url);
        if (Object.prototype.hasOwnProperty.call(DATA, key)) {
            var text = DATA[key];
            return Promise.resolve({
                ok: true,
                status: 200,
                json: function () { return Promise.resolve(JSON.parse(text)); },
                text: function () { return Promise.resolve(text); },
            });
        }
        if (originalFetch) return originalFetch(input, init);
        return Promise.reject(new Error('offline: нет данных для ' + url));
    };
})();
