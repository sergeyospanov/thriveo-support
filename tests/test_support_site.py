from __future__ import annotations

import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "index.html"


def normalized(value: str) -> str:
    return " ".join(value.split())


class SiteParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.stack: list[tuple[str, str | None]] = []
        self.text_by_id: dict[str, list[str]] = {}
        self.language_panels: list[dict[str, str | None]] = []
        self.language_switches: list[str] = []
        self.links: list[dict[str, str | None]] = []
        self.images: list[str] = []
        self.class_counts: dict[str, int] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        element_id = attributes.get("id")
        self.stack.append((tag, element_id))

        for class_name in (attributes.get("class") or "").split():
            self.class_counts[class_name] = self.class_counts.get(class_name, 0) + 1

        if element_id:
            self.text_by_id[element_id] = []

        if "data-language-panel" in attributes:
            self.language_panels.append(attributes)

        if language := attributes.get("data-language-switch"):
            self.language_switches.append(language)

        if tag in {"a", "link"}:
            self.links.append(attributes)

        if tag in {"img", "source"} and (source := attributes.get("src") or attributes.get("srcset")):
            self.images.append(source)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        self.stack.pop()

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                return

    def handle_data(self, data: str) -> None:
        for _, element_id in self.stack:
            if element_id:
                self.text_by_id[element_id].append(data)

    def text(self, element_id: str) -> str:
        return normalized("".join(self.text_by_id.get(element_id, [])))


class SupportSiteContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.html = INDEX_PATH.read_text(encoding="utf-8")
        cls.parser = SiteParser()
        cls.parser.feed(cls.html)

    def test_russian_and_english_are_real_page_content(self) -> None:
        panel_languages = {panel.get("data-language-panel") for panel in self.parser.language_panels}
        self.assertEqual(panel_languages, {"ru", "en"})
        self.assertEqual(set(self.parser.language_switches), {"ru", "en"})
        self.assertTrue(all("hidden" not in panel for panel in self.parser.language_panels))

    def test_faq_matches_the_ios_support_screen_in_both_languages(self) -> None:
        expected = {
            "faq-notifications-question-ru": "Почему напоминания не приходят?",
            "faq-notifications-answer-ru": (
                "Проверьте разрешение уведомлений в Настройках iOS и включено ли "
                "напоминание у активности."
            ),
            "faq-limit-question-ru": "Почему не могу добавить больше активностей?",
            "faq-limit-answer-ru": (
                "Лимит помогает держать список дня собранным. В бесплатной версии можно "
                "держать до 7 активностей. Premium расширяет лимит до 15, чтобы привычки, "
                "срывы и действия для восстановления оставались в одном ритме."
            ),
            "faq-balance-question-ru": "Почему день не закрывается?",
            "faq-balance-answer-ru": (
                "Баланс дня считается как сумма баллов всех выполненных активностей за сегодня. "
                "Негативные активности снижают баланс дня."
            ),
            "faq-notifications-question-en": "Why aren't reminders arriving?",
            "faq-notifications-answer-en": (
                "Check notification permission in iOS Settings and make sure the activity reminder "
                "is enabled."
            ),
            "faq-limit-question-en": "Why can't I add more activities?",
            "faq-limit-answer-en": (
                "The limit keeps your day list focused. Free includes up to 7 active activities. "
                "Premium expands that to 15, so your habits, slip-ups, and recovery actions can "
                "stay in one rhythm."
            ),
            "faq-balance-question-en": "Why isn't the day closing?",
            "faq-balance-answer-en": (
                "Your day balance is the total points from today's completed activities. "
                "Negative activities lower the day balance."
            ),
        }

        actual = {element_id: self.parser.text(element_id) for element_id in expected}
        self.assertEqual(actual, expected)

    def test_new_namespace_contact_and_legal_destinations_are_wired(self) -> None:
        canonical_links = {
            link.get("href")
            for link in self.parser.links
            if link.get("rel") == "canonical"
        }
        hrefs = {link.get("href") for link in self.parser.links}

        self.assertEqual(canonical_links, {"https://sergeyospanov.github.io/thriveo-support/"})
        self.assertIn(
            "https://www.termsfeed.com/live/46c1fd2a-8f8a-4473-89b4-1acf37e6027e",
            hrefs,
        )
        self.assertIn(
            "https://www.apple.com/legal/internet-services/itunes/dev/stdeula/",
            hrefs,
        )
        self.assertTrue(
            any(
                href
                and href.startswith("mailto:ospanov.develop@gmail.com")
                and "subject=" in href
                for href in hrefs
            )
        )

    def test_official_thriveo_assets_replace_placeholder_branding(self) -> None:
        self.assertIn("assets/thriveo-logo-light.png", self.parser.images)
        self.assertIn("assets/thriveo-logo-dark.png", self.parser.images)
        self.assertNotIn("tblkba.github.io", self.html.lower())
        self.assertNotIn("capmino", self.html.lower())

    def test_hero_does_not_repeat_the_header_logo_in_a_balance_panel(self) -> None:
        self.assertEqual(self.parser.class_counts.get("balance-panel", 0), 0)
        self.assertEqual(self.parser.images.count("assets/thriveo-logo-light.png"), 1)
        self.assertEqual(self.parser.images.count("assets/thriveo-logo-dark.png"), 1)

    def test_official_asset_files_exist(self) -> None:
        self.assertTrue((ROOT / "assets" / "thriveo-logo-light.png").is_file())
        self.assertTrue((ROOT / "assets" / "thriveo-logo-dark.png").is_file())
        self.assertTrue((ROOT / "assets" / "thriveo-icon.png").is_file())


if __name__ == "__main__":
    unittest.main()
