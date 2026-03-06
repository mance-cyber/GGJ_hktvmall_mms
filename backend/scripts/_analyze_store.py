"""Quick store analysis for competitor classification"""
import sys, os, asyncio
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.connectors.hktv_api import HKTVApiClient

FRESH_KEYWORDS = {
    '牛': ['牛', '和牛', 'wagyu', 'beef'],
    '豬': ['豬', '黑豚', '豚', 'pork', 'iberico'],
    '雞鴨': ['雞', '鴨', '鵝', 'chicken', 'duck'],
    '三文魚': ['三文魚', '鮭', 'salmon'],
    '魚': ['魚', '鯛', '鰻', '鮪', '吞拿', 'fish', 'tuna'],
    '蝦': ['蝦', '海老', 'shrimp', 'prawn'],
    '蟹': ['蟹', 'crab'],
    '貝/蠔': ['帶子', '貝', '蠔', '蜆', '鮑', 'scallop', 'oyster', 'abalone'],
    '刺身/海膽': ['刺身', '魚生', '海膽', 'uni', 'sashimi'],
    '水果': ['蜜瓜', '蘋果', '草莓', '士多啤梨', '提子', '桃', 'melon', 'fruit'],
}

NON_FRESH_KEYWORDS = [
    '薯片', '零食', '餅', '糖', '朱古力', '醬', '湯', '飲', '麵', '粉',
    '調味', '罐', '即食', '日用', '清潔', '紙巾', '貓', '狗', '寵物',
    '丸', '腸', '餃', '包裝', '杯麵', '茶', '咖啡', '酒', '啤',
]


def classify(name):
    nl = name.lower()
    for cat, kws in FRESH_KEYWORDS.items():
        if any(kw in nl for kw in kws):
            return cat
    if any(kw in nl for kw in NON_FRESH_KEYWORDS):
        return '非生鮮'
    return '其他'


async def analyze_store(store_name):
    client = HKTVApiClient()
    
    # Search by store name
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
    
    print(f"\n{'='*60}")
    print(f"商戶分析: {store_name}")
    print(f"{'='*60}")
    print(f"總商品數: {len(all_products)}")
    
    if not all_products:
        print("⚠️ 未搵到商品，可能需要用 store_code 搜索")
        await client.close()
        return
    
    # Classify
    cats = {}
    samples = {}
    for p in all_products:
        cat = classify(p.name)
        cats[cat] = cats.get(cat, 0) + 1
        if cat not in samples:
            samples[cat] = []
        if len(samples[cat]) < 3:
            price_str = f"${p.price}" if p.price else "N/A"
            samples[cat].append(f"{p.name} ({price_str})")
    
    # Stats
    total = len(all_products)
    fresh_count = sum(v for k, v in cats.items() if k not in ('非生鮮', '其他'))
    non_fresh = cats.get('非生鮮', 0)
    other = cats.get('其他', 0)
    fresh_pct = fresh_count / total * 100 if total else 0
    
    print(f"\n📊 品類分佈:")
    for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
        pct = count / total * 100
        bar = '█' * int(pct / 2)
        emoji = '✅' if cat not in ('非生鮮', '其他') else '❌' if cat == '非生鮮' else '❓'
        print(f"  {emoji} {cat}: {count} ({pct:.0f}%) {bar}")
        for s in samples.get(cat, []):
            print(f"      └ {s}")
    
    print(f"\n📈 生鮮比例: {fresh_count}/{total} ({fresh_pct:.0f}%)")
    
    # Tier recommendation
    print(f"\n🏷️ 分級建議:")
    if fresh_pct >= 60:
        print(f"  → Tier 1 (直接對手) — 生鮮佔 {fresh_pct:.0f}%，高度重疊")
    elif fresh_pct >= 30:
        print(f"  → Tier 2 (品類重疊) — 生鮮佔 {fresh_pct:.0f}%，有一定競爭")
    elif fresh_pct >= 10:
        print(f"  → Tier 3 (參考) — 生鮮佔 {fresh_pct:.0f}%，少量重疊")
    else:
        print(f"  → 不追蹤 — 生鮮佔 {fresh_pct:.0f}%，基本無競爭關係")
    
    # GoGoJap overlap analysis
    overlap_cats = set()
    gogojap_cats = {'牛', '魚', '三文魚', '蝦', '蟹', '貝/蠔', '刺身/海膽'}
    for cat in cats:
        if cat in gogojap_cats:
            overlap_cats.add(cat)
    
    if overlap_cats:
        print(f"  與 GoGoJap 重疊品類: {', '.join(overlap_cats)}")
    
    await client.close()


async def discover_competitors():
    """Search for potential competitors using fresh food keywords"""
    client = HKTVApiClient()
    
    search_terms = [
        '和牛', 'A5和牛', '日本和牛',
        '三文魚刺身', '吞拿魚刺身',
        '帶子', '海膽', '日本蝦',
        '急凍牛肉', '急凍海鮮',
        '日本水果', '日本蜜瓜',
    ]
    
    store_counts = {}
    store_samples = {}
    
    for term in search_terms:
        products = await client.search_products(term, page_size=50)
        for p in products:
            store = p.store_name or 'Unknown'
            if store == 'Unknown':
                continue
            store_counts[store] = store_counts.get(store, 0) + 1
            if store not in store_samples:
                store_samples[store] = []
            if len(store_samples[store]) < 3:
                store_samples[store].append(p.name)
    
    print(f"\n{'='*60}")
    print(f"潛在競爭商戶（按生鮮商品出現次數排序）")
    print(f"{'='*60}")
    
    for store, count in sorted(store_counts.items(), key=lambda x: -x[1])[:20]:
        print(f"\n🏪 {store} — {count} 次出現")
        for s in store_samples.get(store, []):
            print(f"   └ {s}")
    
    await client.close()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--store', help='分析指定商戶')
    parser.add_argument('--discover', action='store_true', help='發現新商戶')
    args = parser.parse_args()
    
    if args.store:
        asyncio.run(analyze_store(args.store))
    elif args.discover:
        asyncio.run(discover_competitors())
    else:
        print("Usage: python _analyze_store.py --store '森源屋'")
        print("       python _analyze_store.py --discover")
