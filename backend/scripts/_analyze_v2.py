"""Analyze a store's products for competitor classification"""
import sys, os, asyncio
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

from app.connectors.hktv_api import HKTVApiClient

FRESH = {
    'A5/A4 和牛': ['a5', 'a4', '和牛', 'wagyu'],
    '其他牛肉': ['牛', 'beef', '安格斯'],
    '豬/豚': ['豬', '黑豚', '豚', 'pork', 'iberico'],
    '雞鴨': ['雞', '鴨', '鵝', 'chicken', 'duck'],
    '三文魚': ['三文魚', '鮭', 'salmon'],
    '其他魚': ['魚', '鯛', '鰻', '鮪', '吞拿', 'fish', 'tuna'],
    '蝦': ['蝦', '海老', 'shrimp', 'prawn'],
    '蟹': ['蟹', 'crab'],
    '貝/蠔': ['帶子', '貝', '蠔', '蜆', '鮑', 'scallop', 'oyster', 'abalone'],
    '刺身': ['刺身', '魚生', 'sashimi'],
    '海膽': ['海膽', 'uni'],
    '水果': ['蜜瓜', '蘋果', '草莓', '提子', '桃', 'melon', 'fruit', '芒果', '葡萄'],
}
NON_FRESH = [
    '薯片', '零食', '餅乾', '糖', '朱古力', '醬油', '湯底', '飲品', '麵', '粉',
    '調味', '罐頭', '即食', '日用品', '清潔', '紙巾', '寵物', '貓', '狗',
    '茶', '咖啡', '酒', '啤', '丸', '腸', '餃', '包', '杯麵', '雪糕',
]


def classify(name):
    nl = name.lower()
    for cat, kws in FRESH.items():
        if any(kw in nl for kw in kws):
            return cat
    if any(kw in nl for kw in NON_FRESH):
        return 'non-fresh'
    return 'other'


async def analyze(store_name):
    client = HKTVApiClient()

    # Try store name search first
    all_products = []
    page = 0
    while True:
        products = await client.search_by_store(store_name, page_size=100, page=page)
        if not products:
            break
        all_products.extend(products)
        if len(products) < 100:
            break
        page += 1

    # Fallback to keyword search
    if not all_products:
        all_products = await client.search_products(store_name, page_size=100)

    print(f"\n{'='*60}")
    print(f"商戶: {store_name}")
    print(f"總商品: {len(all_products)}")
    print(f"{'='*60}")

    if not all_products:
        print("未搵到商品")
        await client.close()
        return

    cats = {}
    samples = {}
    price_lists = {}
    for p in all_products:
        cat = classify(p.name)
        cats[cat] = cats.get(cat, 0) + 1
        if cat not in samples:
            samples[cat] = []
        if len(samples[cat]) < 3:
            px = f"${p.price}" if p.price else "N/A"
            samples[cat].append(f"{p.name[:45]} ({px})")
        if cat not in price_lists:
            price_lists[cat] = []
        if p.price:
            price_lists[cat].append(float(p.price))

    total = len(all_products)
    fresh = sum(v for k, v in cats.items() if k not in ('non-fresh', 'other'))
    non_fresh = cats.get('non-fresh', 0)
    other = cats.get('other', 0)
    fresh_pct = fresh / total * 100 if total else 0

    print(f"\n--- 品類分佈 ---")
    for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
        pct = count / total * 100
        pl = price_lists.get(cat, [])
        avg = sum(pl) / len(pl) if pl else 0
        bar = '#' * int(pct / 2)
        tag = "FRESH" if cat not in ('non-fresh', 'other') else "-----"
        print(f"  [{tag}] {cat}: {count} ({pct:.0f}%) avg=${avg:.0f} {bar}")
        for s in samples.get(cat, []):
            print(f"         - {s}")

    print(f"\n--- 統計 ---")
    print(f"  生鮮: {fresh}/{total} ({fresh_pct:.0f}%)")
    print(f"  非生鮮: {non_fresh} ({non_fresh/total*100:.0f}%)")
    print(f"  其他: {other} ({other/total*100:.0f}%)")

    # GoGoJap overlap
    gogojap_cats = {'A5/A4 和牛', '其他牛肉', '其他魚', '三文魚', '蝦', '蟹', '貝/蠔', '刺身', '海膽'}
    overlap = [c for c in cats if c in gogojap_cats]

    print(f"\n--- 分級建議 ---")
    print(f"  與 GoGoJap 重疊品類: {', '.join(overlap) if overlap else '無'}")
    if fresh_pct >= 60:
        print(f"  => Tier 1 (直接對手) -- 生鮮佔 {fresh_pct:.0f}%")
    elif fresh_pct >= 30:
        print(f"  => Tier 2 (品類重疊) -- 生鮮佔 {fresh_pct:.0f}%")
    elif fresh_pct >= 10:
        print(f"  => Tier 3 (參考) -- 生鮮佔 {fresh_pct:.0f}%")
    else:
        print(f"  => 不追蹤 -- 生鮮佔 {fresh_pct:.0f}%")

    await client.close()


async def discover():
    """Find potential competitors via fresh food keyword searches"""
    client = HKTVApiClient()

    terms = [
        '和牛', 'A5和牛', '日本和牛',
        '三文魚刺身', '吞拿魚',
        '帶子', '海膽', '日本蝦',
        '急凍牛肉', '急凍海鮮',
        '日本蜜瓜', '日本水果',
        '黑豚', '日本豚',
    ]

    store_hits = {}  # store -> set of matched terms
    store_samples = {}

    for term in terms:
        products = await client.search_products(term, page_size=50)
        for p in products:
            store = p.store_name or 'Unknown'
            if store == 'Unknown':
                continue
            if store not in store_hits:
                store_hits[store] = set()
                store_samples[store] = []
            store_hits[store].add(term)
            if len(store_samples[store]) < 4:
                store_samples[store].append(p.name[:50])

    print(f"\n{'='*60}")
    print(f"潛在競爭商戶（按覆蓋關鍵詞數排序）")
    print(f"{'='*60}")

    sorted_stores = sorted(store_hits.items(), key=lambda x: len(x[1]), reverse=True)
    for store, terms_matched in sorted_stores[:25]:
        print(f"\n  {store} -- {len(terms_matched)} 個關鍵詞命中")
        print(f"    命中: {', '.join(sorted(terms_matched))}")
        for s in store_samples.get(store, []):
            print(f"    - {s}")

    await client.close()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--store', help='Analyze a specific store')
    parser.add_argument('--discover', action='store_true', help='Discover new competitors')
    args = parser.parse_args()

    if args.store:
        asyncio.run(analyze(args.store))
    elif args.discover:
        asyncio.run(discover())
    else:
        print("Usage:")
        print("  python _analyze_v2.py --store '森源屋'")
        print("  python _analyze_v2.py --discover")
