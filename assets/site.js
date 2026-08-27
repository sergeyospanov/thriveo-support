const SUPPORTED_LANGUAGES = new Set(["ru", "en"]);

const PAGE_METADATA = {
  ru: {
    title: "Поддержка Thriveo",
    description:
      "Официальная поддержка Thriveo: ответы о напоминаниях, лимите активностей и балансе дня.",
    main: "main-ru",
  },
  en: {
    title: "Thriveo Support",
    description:
      "Official Thriveo support: answers about reminders, activity limits, and the day balance.",
    main: "main-en",
  },
};

export function resolveLanguage({ search = "", languages = [] } = {}) {
  const requested = new URLSearchParams(search).get("lang");
  if (SUPPORTED_LANGUAGES.has(requested)) {
    return requested;
  }

  const hasRussianPreference = languages.some(
    (language) => language.toLowerCase().split("-")[0] === "ru",
  );
  return hasRussianPreference ? "ru" : "en";
}

function setLanguage(language, { updateURL = false } = {}) {
  const selected = SUPPORTED_LANGUAGES.has(language) ? language : "en";
  const metadata = PAGE_METADATA[selected];

  document.documentElement.lang = selected;

  document.querySelectorAll("[data-language-panel]").forEach((panel) => {
    const isActive = panel.dataset.languagePanel === selected;
    panel.classList.toggle("is-active", isActive);
    panel.hidden = !isActive;
  });

  document.querySelectorAll("[data-language-copy]").forEach((copy) => {
    const isActive = copy.dataset.languageCopy === selected;
    copy.classList.toggle("is-active", isActive);
    copy.hidden = !isActive;
  });

  document.querySelectorAll("[data-language-switch]").forEach((button) => {
    const isActive = button.dataset.languageSwitch === selected;
    button.classList.toggle("is-active", isActive);
    button.setAttribute("aria-pressed", String(isActive));
  });

  document.title = metadata.title;
  document.querySelector('meta[name="description"]')?.setAttribute("content", metadata.description);
  document.querySelector(".skip-link")?.setAttribute("href", `#${metadata.main}`);

  if (updateURL) {
    const url = new URL(window.location.href);
    url.searchParams.set("lang", selected);
    window.history.replaceState({}, "", `${url.pathname}${url.search}${url.hash}`);
  }
}

function startLanguageSwitcher() {
  document.documentElement.classList.add("js-ready");

  const selected = resolveLanguage({
    search: window.location.search,
    languages: Array.from(window.navigator.languages ?? [window.navigator.language]),
  });
  setLanguage(selected);

  document.querySelectorAll("[data-language-switch]").forEach((button) => {
    button.addEventListener("click", () => {
      setLanguage(button.dataset.languageSwitch, { updateURL: true });
    });
  });
}

if (typeof document !== "undefined" && typeof window !== "undefined") {
  startLanguageSwitcher();
}
