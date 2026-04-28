# 🌍 MCP Weather Agent (Israel & USA)

סוכן חכם המבוסס על פרוטוקול MCP, המסוגל לבדוק מזג אוויר בזמן אמת בישראל (באמצעות אוטומציה של Playwright) ובארה"ב.

## 🚀 איך להריץ?
1. התקנת דרישות: `uv pip install -r requirements.txt`
2. הגדרת משתני סביבה: צרו קובץ `.env` עם `ANTHROPIC_API_KEY` או `GROQ_API_KEY`.
3. הרצת השרתים: `uv run weather_Israel.py` ו-`uv run weather_USA.py`.
4. הרצת ה-Host: `uv run host.py`.

## 📸 הצצה לפעולת הסוכן (Demo)

כך נראה הדפדפן (Playwright) בזמן שהסוכן שולף נתונים מאתר מזג האוויר בישראל:

![מזג האוויר בחיפה - סריקת אתר](air.png)

*בתמונה: הסוכן איתר בהצלחה טמפרטורה של 20°C בחוף הסטודנטים בחיפה.*
## 🤖 דוגמאות לשאלות
- "מה מזג האוויר בחיפה עכשיו?"
- "האם יש התראות מזג אוויר בניו יורק?"
- "האם כדאי לקחת מטריה מחר לירושלים?"

## 🛠 טכנולוגיות
- Python & Asyncio
- MCP SDK (Model Context Protocol)
- Playwright (Web Scraping)
- Groq / Anthropic API
