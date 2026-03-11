'use client';

// ==================== Clawdbot Test Page (Simplified) ====================
// Purpose: Test clawdbot scraping feature

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

  // Check health status
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

  // Scrape products
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
      setError(err instanceof Error ? err.message : 'Scraping failed');
    } finally {
      setLoading(false);
    }
  };

  // Check health status on page load
  useEffect(() => {
    checkHealth();
  }, []);

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Page title */}
      <div>
        <h1 className="text-3xl font-bold">Clawdbot Test Panel</h1>
        <p className="text-gray-600 mt-2">
          Test clawdbot browser automation scraping feature
        </p>
      </div>

      {/* Health Status Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            Clawdbot Service Status
            {isConnected ? (
              <Badge className="bg-green-500">Connected</Badge>
            ) : (
              <Badge variant="destructive">Disconnected</Badge>
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
            Refresh Status
          </Button>

          {!isConnected && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded">
              <p className="text-sm text-red-800 font-semibold">
                Clawdbot is not running
              </p>
              <p className="text-sm text-red-600 mt-2">
                Please confirm clawdbot is running:
              </p>
              <code className="block mt-2 p-2 bg-gray-100 rounded text-xs">
                cd clawdbot && node scripts/run-node.mjs gateway --port 18789
              </code>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Test Feature */}
      <Card>
        <CardHeader>
          <CardTitle>Scrape HKTVmall Product Information</CardTitle>
          <CardDescription>
            Enter product page URL to automatically extract product information
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="product-url">Product URL</Label>
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
            {loading ? 'Scraping...' : 'Start Scraping'}
          </Button>

          {error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          {result && (
            <div className="mt-4">
              <h3 className="font-semibold mb-2">Scrape Result:</h3>
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
