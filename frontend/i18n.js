const i18n = {
  locale: 'en',
  translations: {},
  async load(locale) {
    this.locale = locale;
    try {
      const res = await fetch(`locales/${locale}.json`);
      if (!res.ok) throw new Error('Failed to load locale data');
      this.translations = await res.json();
      this.apply();
    } catch (e) {
      console.error('i18n load error:', e);
    }
  },
  apply() {
    // Translate elements with data-i18n
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      const txt = this.translations[key];
      if (txt !== undefined) el.textContent = txt;
    });
  }
};
// Expose globally
window.i18n = i18n;