from mcp.server.fastmcp import FastMCP
from playwright.async_api import async_playwright

mcp = FastMCP("weather-Israel")

# אובייקט גלובלי לשמירת ה-State של הדפדפן בין קריאות לכלים
browser_state = {
    "playwright": None,
    "browser": None,
    "page": None
}

async def get_page():
    """פונקציית עזר לניהול מופע יחיד של דפדפן"""
    if browser_state["page"] is None:
        browser_state["playwright"] = await async_playwright().start()
        # headless=False מאפשר לנו לראות את הדפדפן פועל בזמן אמת
        browser_state["browser"] = await browser_state["playwright"].chromium.launch(headless=False)
        browser_state["page"] = await browser_state["browser"].new_page()
    return browser_state["page"]

@mcp.tool()
async def open_weather_forecast_israel():
    """פותח את אתר Weather2day ומכין אותו לחיפוש"""
    page = await get_page()
    await page.goto("https://www.weather2day.co.il/forecast")
    return "האתר נפתח. כעת אפשר להזין שם עיר ב-enter_weather_forecast_city_israel."

@mcp.tool()
async def enter_weather_forecast_city_israel(city_name: str):
    """מזין את שם העיר בשדה החיפוש ומחכה להצעות"""
    page = await get_page()
    selector = "#city_search_forecast" # הסלקטור המדויק באתר
    await page.wait_for_selector(selector)
    await page.fill(selector, city_name)
    # מחכים רגע שה-Autocomplete יופיע
    await page.wait_for_selector(".autocomplete-items")
    return f"העיר '{city_name}' הוזנה. השלב הבא: לבחור אותה מהרשימה."

@mcp.tool()
async def select_weather_forecast_city_israel():
    """בוחר את התוצאה הראשונה ונוחת בדף התחזית"""
    page = await get_page()
    # לחיצה על הפריט הראשון ברשימת הדיב הנפתח
    await page.click(".autocomplete-items div:first-child")
    await page.wait_for_load_state("networkidle")
    return f"העיר נבחרה. כתובת הדף הנוכחי: {page.url}"

@mcp.tool()
async def get_forecast_content_israel():
    """שלב ב': מחלץ את הטקסט של התחזית מהדף עבור ה-LLM"""
    page = await get_page()
    # חילוץ תוכן מהאלמנט הראשי של התחזית
    # האתר משתמש ב-ID או Class ספציפי לטבלת התחזית
    content = await page.inner_text(".forecast-wrap")
    return f"מידע על התחזית שנמצא בדף:\n{content[:2000]}"

def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()