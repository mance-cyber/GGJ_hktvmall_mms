'use client';

// ==================== Clawdbot 測試頁面 (簡化版) ====================
// 用途: 測試 clawdbot 抓取功能

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';

export default function ClawdbotTestPage() {
  const [isConnected, setIsConnected] = useState(false);
  const [productUrl, setProductUrl] = useState('');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 檢查健康狀態
  const checkHealth = async () => {
    try {
      const response = await fetch('/api/v1/scrape/clawdbot');
      const data = await response.json();
      setIsConnected(data.status === 'connected');
    } catch (err) {
      setIsConnected(false);
      console.error('Health check failed:', err);
    }
  };

  // 抓取商品
  const handleScrapeProduct = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch('/api/v1/scrape/clawdbot', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'scrape_product',
          params: { url: productUrl },
        }),
      });

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : '抓取失敗');
    } finally {
      setLoading(false);
    }
  };

  // 頁面加載時檢查健康狀態
  useEffect(() => {
    checkHealth();
  }, []);

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* 頁面標題 */}
      <div>
        <h1 className="text-3xl font-bold">Clawdbot 測試面板</h1>
        <p className="text-gray-600 mt-2">
          測試 clawdbot 瀏覽器自動化抓取功能
        </p>
      </div>

      {/* 健康狀態卡片 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            Clawdbot 服務狀態
            {isConnected ? (
              <Badge className="bg-green-500">已連接</Badge>
            ) : (
              <Badge variant="destructive">未連接</Badge>
            )}
          </CardTitle>
          <CardDescription>
            WebSocket Gateway: ws://127.0.0.1:18789
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button
            onClick={checkHealth}
            variant="outline"
            size="sm"
            className="w-full"
          >
            刷新狀態
          </Button>

          {!isConnected && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded">
              <p className="text-sm text-red-800 font-semibold">
                Clawdbot 未運行
              </p>
              <p className="text-sm text-red-600 mt-2">
                請確認 clawdbot 已啟動:
              </p>
              <code className="block mt-2 p-2 bg-gray-100 rounded text-xs">
                cd clawdbot && node scripts/run-node.mjs gateway --port 18789
              </code>
            </div>
          )}
        </CardContent>
      </Card>

      {/* 測試功能 */}
      <Card>
        <CardHeader>
          <CardTitle>抓取 HKTVmall 商品資訊</CardTitle>
          <CardDescription>
            輸入商品頁面 URL，自動提取商品資訊
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="product-url">商品 URL</Label>
            <Input
              id="product-url"
              placeholder="https://www.hktvmall.com/..."
              value={productUrl}
              onChange={(e) => setProductUrl(e.target.value)}
            />
          </div>

          <Button
            onClick={handleScrapeProduct}
            disabled={!isConnected || loading || !productUrl}
            className="w-full"
          >
            {loading ? '抓取中...' : '開始抓取'}
          </Button>

          {error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          {result && (
            <div className="mt-4">
              <h3 className="font-semibold mb-2">抓取結果:</h3>
              <pre className="bg-gray-100 p-4 rounded-lg overflow-auto max-h-96 text-sm">
                {JSON.stringify(result, null, 2)}
              </pre>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
