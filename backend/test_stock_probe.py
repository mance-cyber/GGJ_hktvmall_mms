import asyncio
from app.services.stock_prober import probe_stock, probe_stocks_batch
import httpx

async def test():
    # Test single SKU
    async with httpx.AsyncClient() as client:
        r = await probe_stock('S2461001_S_KM0019', client)
        print(f'SKU: {r.sku}')
        print(f'Stock: {r.stock_level}')
        print(f'In stock: {r.in_stock}')
        print(f'Error: {r.error}')
    
    # Test batch with a few SKUs
    test_skus = ['S2461001_S_KM0019', 'S2461001_S_KM0058', 'S2461001_S_KM0112']
    results = await probe_stocks_batch(test_skus, concurrency=2, delay=0.5)
    print(f'\nBatch results:')
    for sku, r in results.items():
        print(f'  {sku}: stock={r.stock_level}, in_stock={r.in_stock}, error={r.error}')

asyncio.run(test())
