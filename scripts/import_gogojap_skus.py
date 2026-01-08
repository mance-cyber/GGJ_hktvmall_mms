#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================
# GogoJap SKU CSV 導入腳本
# Market Response Center (MRC) - Phase 1
# =============================================
"""
將 GogoJap-SKU list.csv 導入 PostgreSQL products 表

CSV 欄位映射:
  大分類 -> category_main
  小分類 -> category_sub
  產品編號 -> sku (若空則自動生成)
  中文品名 -> name_zh, name (主名稱)
  日文品名 -> name_ja
  英文品名/規格 -> name_en
  單位 -> unit
  季節/備註 -> season_tag
"""

import csv
import uuid
import sys
import os
import io
from pathlib import Path
from datetime import datetime

# Windows 控制台 UTF-8 支援
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 添加 backend 到 path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))


def generate_sku(category_main: str, category_sub: str, index: int) -> str:
    """生成唯一 SKU 碼"""
    category_codes = {
        "飛機貨(鮮活)": "AIR",
        "乾貨/調味": "DRY",
        "急凍/冷藏": "FRZ",
        "雜項": "MIS",
        "米/穀類": "RIC",
    }
    sub_codes = {
        "鮮魚/活口海鮮": "FSH",
        "小型魚/細魚": "SMF",
        "貝類/軟體海鮮": "SHL",
        "蝦蟹類": "CRU",
        "海膽/魚卵/肝": "ROE",
        "加工/其他": "PRC",
        "野菜/果物": "VEG",
        "漬物": "PKL",
        "肉類": "MET",
        "粉類": "FLR",
        "紫菜/海草/昆布": "SEA",
        "削節/湯包": "SOP",
        "魚乾": "DFS",
        "醬油/豉油": "SOY",
        "麵豉/味噌": "MSO",
        "醋": "VIN",
        "味醂/酒": "SAK",
        "油": "OIL",
        "調味/醬汁": "SAS",
        "鹽/糖": "SSG",
        "和牛/豚": "WAG",
        "廚具/清潔": "KIT",
        "茶類": "TEA",
        "日本米": "JRC",
        "雜項": "MIS",
    }
    
    cat_code = category_codes.get(category_main, "XXX")
    sub_code = sub_codes.get(category_sub, "XXX")
    
    return f"GGJ-{cat_code}-{sub_code}-{index:04d}"


def clean_text(text: str) -> str:
    """清理文本，移除多餘空白"""
    if not text:
        return None
    cleaned = text.strip()
    return cleaned if cleaned else None


def normalize_season(season: str) -> str:
    """標準化季節標籤"""
    if not season:
        return "ALL"
    
    season = season.upper().strip()
    
    season_map = {
        "ALL": "ALL",
        "WINTER": "WINTER",
        "SPRING": "SPRING",
        "SUMMER": "SUMMER",
        "AUTUMN": "AUTUMN",
        "FALL": "AUTUMN",
    }
    
    if season in season_map:
        return season_map[season]
    
    return season


def parse_csv(csv_path: str) -> list:
    """解析 CSV 文件"""
    products = []
    
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        
        for idx, row in enumerate(reader, start=1):
            if not any(row.values()):
                continue
            
            category_main = clean_text(row.get('大分類', ''))
            category_sub = clean_text(row.get('小分類', ''))
            product_code = clean_text(row.get('產品編號', ''))
            name_zh = clean_text(row.get('中文品名', ''))
            name_ja = clean_text(row.get('日文品名', ''))
            name_en = clean_text(row.get('英文品名/規格', ''))
            unit = clean_text(row.get('單位', ''))
            season_raw = clean_text(row.get('季節/備註', ''))
            
            if not name_zh:
                print(f"[SKIP] Row {idx}: Missing Chinese name")
                continue
            
            if product_code:
                sku = f"GGJ-{product_code}"
            else:
                sku = generate_sku(category_main, category_sub, idx)
            
            season_tag = normalize_season(season_raw)
            
            product = {
                'id': str(uuid.uuid4()),
                'sku': sku,
                'name': name_zh,
                'name_zh': name_zh,
                'name_ja': name_ja,
                'name_en': name_en,
                'category': f"{category_main} > {category_sub}" if category_sub else category_main,
                'category_main': category_main,
                'category_sub': category_sub,
                'unit': unit,
                'season_tag': season_tag,
                'source': 'gogojap_csv',
                'status': 'active',
                'stock_quantity': 0,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat(),
            }
            
            products.append(product)
    
    return products


def export_sql(products: list, output_path: str):
    """導出為 SQL INSERT 語句"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("-- GogoJap SKU Import SQL\n")
        f.write(f"-- Generated: {datetime.now().isoformat()}\n")
        f.write(f"-- Total: {len(products)} records\n\n")
        
        f.write("BEGIN;\n\n")
        
        for p in products:
            def sql_val(v):
                if v is None:
                    return "NULL"
                return "'" + str(v).replace("'", "''") + "'"
            
            f.write(f"""INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '{p['id']}',
    {sql_val(p['sku'])},
    {sql_val(p['name'])},
    {sql_val(p['name_zh'])},
    {sql_val(p['name_ja'])},
    {sql_val(p['name_en'])},
    {sql_val(p['category'])},
    {sql_val(p['category_main'])},
    {sql_val(p['category_sub'])},
    {sql_val(p['unit'])},
    {sql_val(p['season_tag'])},
    {sql_val(p['source'])},
    {sql_val(p['status'])},
    {p['stock_quantity']},
    '{p['created_at']}',
    '{p['updated_at']}'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

""")
        
        f.write("COMMIT;\n")


def export_json(products: list, output_path: str):
    """導出為 JSON"""
    import json
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)


def main():
    """主函數"""
    print("=" * 50)
    print("GogoJap SKU CSV Import Tool")
    print("Market Response Center (MRC)")
    print("=" * 50)
    
    project_root = Path(__file__).parent.parent
    csv_path = project_root / "products" / "GogoJap-SKU list.csv"
    sql_output = project_root / "scripts" / "gogojap_skus.sql"
    json_output = project_root / "scripts" / "gogojap_skus.json"
    
    if not csv_path.exists():
        print(f"[ERROR] CSV not found: {csv_path}")
        sys.exit(1)
    
    print(f"\n[READ] CSV: {csv_path}")
    products = parse_csv(str(csv_path))
    
    print(f"[OK] Parsed: {len(products)} products")
    
    # Statistics
    categories = {}
    for p in products:
        cat = p['category_main']
        categories[cat] = categories.get(cat, 0) + 1
    
    print("\n[STATS] Category breakdown:")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"   {cat}: {count}")
    
    # Export
    print(f"\n[WRITE] SQL: {sql_output}")
    export_sql(products, str(sql_output))
    
    print(f"[WRITE] JSON: {json_output}")
    export_json(products, str(json_output))
    
    print("\n" + "=" * 50)
    print("[DONE] Import preparation complete!")
    print("=" * 50)
    print("\nNext steps:")
    print("  1. Run Migration: cd backend && alembic upgrade head")
    print("  2. Import SQL: psql -d <database> -f scripts/gogojap_skus.sql")


if __name__ == "__main__":
    main()
