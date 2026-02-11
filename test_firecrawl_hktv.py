#!/usr/bin/env python3
"""
本地測試腳本：驗證 HKTVmall 搜索和 URL 提取邏輯

用法：
    python test_firecrawl_hktv.py

需要：
    pip install firecrawl-py python-dotenv
"""

import os
import re
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 測試關鍵詞
TEST_QUERY = "豬肉"
SEARCH_URL = f"https://www.hktvmall.com/hktv/zh/search?q={TEST_QUERY}"

print(f"🔍 測試搜索關鍵詞: {TEST_QUERY}")
print(f"📍 搜索 URL: {SEARCH_URL}")
print("=" * 60)

# ==================== Step 1: 測試 Firecrawl 連接 ====================
print("\n[Step 1] 測試 Firecrawl API 連接...")

try:
    from firecrawl import FirecrawlApp

    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        print("❌ FIRECRAWL_API_KEY 未設定")
        print("請在 .env 文件中設定：FIRECRAWL_API_KEY=fc-xxx")
        exit(1)

    app = FirecrawlApp(api_key=api_key)
    print(f"✅ Firecrawl 初始化成功")
    print(f"📌 API Key: {api_key[:10]}...{api_key[-4:]}")

except Exception as e:
    print(f"❌ Firecrawl 初始化失敗: {e}")
    exit(1)

# ==================== Step 2: 抓取搜索頁面 ====================
print(f"\n[Step 2] 抓取 HKTVmall 搜索頁面...")

try:
    # Firecrawl v1.x 使用 scrape() 方法
    # 增加等待時間，並等待商品容器加載
    result = app.scrape(
        url=SEARCH_URL,
        formats=['html'],
        wait_for=15000  # 等待 15 秒讓 JS 渲染
    )

    # 檢查返回結構
    if isinstance(result, dict):
        html = result.get("html", "")
        if not html:
            # 嘗試其他可能的鍵
            html = result.get("content", "")
            html = result.get("markdown", "") if not html else html
    else:
        # 可能是對象
        html = getattr(result, 'html', '')
        if not html:
            html = getattr(result, 'content', '')

    print(f"✅ 抓取成功")
    print(f"📊 HTML 長度: {len(html)} 字符")
    print(f"📊 包含 'href=': {('href=' in html)}")
    print(f"📊 包含 '/p/': {('/p/' in html)}")

    # 保存 HTML 到文件以便檢查
    with open("hktv_search_result.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"💾 完整 HTML 已保存到: hktv_search_result.html")

    # Debug: 顯示返回的鍵
    if isinstance(result, dict):
        print(f"🔍 返回的鍵: {list(result.keys())}")

except Exception as e:
    print(f"❌ 抓取失敗: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# ==================== Step 3: 提取商品 URL ====================
print(f"\n[Step 3] 提取商品 URL...")

# HKTVmall 商品鏈接模式（放寬版）
patterns = [
    r'href="([^"]*?/p/[A-Z]\d+[^"]*)"',           # /p/H12345, /p/B12345 等
    r'href="([^"]*hktvmall\.com[^"]*[A-Z]\d{6,}[^"]*)"',  # 完整 URL
    r'data-href="([^"]*?/p/[A-Z]\d+[^"]*)"',      # data-href 屬性
    r'onclick="[^"]*(/p/[A-Z]\d+)[^"]*"',         # onclick 中的連結
    r'href="([^"]*?/product/[^"]*)"',             # /product/ 格式
]

product_urls = set()

for i, pattern in enumerate(patterns, 1):
    matches = re.findall(pattern, html, re.IGNORECASE)
    if matches:
        print(f"  Pattern {i} 找到 {len(matches)} 個匹配")
        for match in matches[:3]:  # 只顯示前 3 個
            # 補全相對路徑
            if match.startswith("/"):
                full_url = "https://www.hktvmall.com" + match
            elif match.startswith("http"):
                full_url = match
            else:
                continue

            # 清理 URL
            full_url = full_url.split("?")[0]
            product_urls.add(full_url)
            print(f"    → {full_url}")

print(f"\n✅ 總共提取到 {len(product_urls)} 個唯一商品 URL")

if len(product_urls) == 0:
    print("\n❌ 沒有提取到任何 URL！")
    print("\n🔍 讓我們看看 HTML 樣本（前 2000 字符）：")
    print("=" * 60)
    print(html[:2000])
    print("=" * 60)
    print("\n💡 建議：")
    print("1. 檢查 hktv_search_result.html 看完整頁面結構")
    print("2. 手動在瀏覽器訪問搜索 URL 確認有結果")
    print("3. 可能需要更長的 waitFor 時間")
else:
    print("\n✅ URL 提取成功！樣本：")
    for url in list(product_urls)[:5]:
        print(f"  • {url}")

# ==================== Step 4: 測試總結 ====================
print("\n" + "=" * 60)
print("📊 測試總結")
print("=" * 60)
print(f"✅ Firecrawl 連接: 成功")
print(f"✅ 頁面抓取: 成功 ({len(html)} 字符)")
print(f"{'✅' if len(product_urls) > 0 else '❌'} URL 提取: {len(product_urls)} 個")
print("=" * 60)

if len(product_urls) > 0:
    print("\n🎉 測試成功！可以部署到 Zeabur 了")
else:
    print("\n⚠️  需要進一步調查 HTML 結構")
