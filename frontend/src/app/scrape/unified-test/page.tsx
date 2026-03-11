'use client';

// ==================== Unified Scraper Test Page ====================
// Purpose: Test hybrid architecture auto-switching feature
// Path: /scrape/unified-test

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';

interface ScraperInfo {
  type: string;
  status: string;
  endpoint: string;
  hasApiKey: boolean;
  environment: string;
}

export default function UnifiedScraperTestPage() {
  const [scraperInfo, setScraperInfo] = useState<ScraperInfo | null>(null);
  const [loading, setLoading] = useState(false);
  const [testUrl, setTestUrl] = useState(
    'https://www.hktvmall.com/hktv/zh/main/gogojap-123456'
  );
  const [result, setResult] = useState<any>(null);

  // ==================== Fetch Scraper Configuration ====================

  useEffect(() => {
    fetchScraperInfo();
  }, []);

  const fetchScraperInfo = async () => {
    try {
      const response = await fetch('/api/v1/scrape');
      const data = await response.json();

      if (data.success) {
        setScraperInfo(data.scraper);
      }
    } catch (error) {
      console.error('Failed to fetch scraper info:', error);
    }
  };

  // ==================== Test Scraping ====================

  const handleTestScrape = async () => {
    if (!testUrl) {
      alert('Please enter a test URL');
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const response = await fetch('/api/v1/scrape', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'scrape_url',
          params: { url: testUrl },
        }),
      });

      const data = await response.json();
      setResult(data);
    } catch (error) {
      setResult({
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      });
    } finally {
      setLoading(false);
    }
  };

  // ==================== Rendering ====================

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'connected':
        return 'bg-green-500';
      case 'disconnected':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getScraperBadgeColor = (type: string) => {
    return type === 'clawdbot' ? 'bg-blue-500' : 'bg-orange-500';
  };

  return (
    <div className="container mx-auto p-8 space-y-6">
      {/* Page Title */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Unified Scraper Test</h1>
          <p className="text-muted-foreground mt-1">
            Test hybrid architecture auto-switching feature
          </p>
        </div>
        <Button onClick={fetchScraperInfo} variant="outline">
          🔄 Refresh Status
        </Button>
      </div>

      {/* Scraper Configuration Info */}
      <Card>
        <CardHeader>
          <CardTitle>Current Scraper Configuration</CardTitle>
        </CardHeader>
        <CardContent>
          {scraperInfo ? (
            <div className="space-y-4">
              {/* Scraper Type */}
              <div className="flex items-center gap-4">
                <span className="text-sm font-medium w-24">Scraper Type:</span>
                <Badge className={getScraperBadgeColor(scraperInfo.type)}>
                  {scraperInfo.type === 'clawdbot' ? '🤖 Clawdbot' : '🔥 Firecrawl'}
                </Badge>
              </div>

              {/* Environment */}
              <div className="flex items-center gap-4">
                <span className="text-sm font-medium w-24">Environment:</span>
                <Badge variant="outline">{scraperInfo.environment}</Badge>
              </div>

              {/* Connection Status */}
              <div className="flex items-center gap-4">
                <span className="text-sm font-medium w-24">Status:</span>
                <div className="flex items-center gap-2">
                  <div
                    className={`h-3 w-3 rounded-full ${getStatusColor(
                      scraperInfo.status
                    )}`}
                  />
                  <span className="text-sm">
                    {scraperInfo.status === 'connected' ? 'Connected' : 'Disconnected'}
                  </span>
                </div>
              </div>

              {/* Endpoint */}
              <div className="flex items-center gap-4">
                <span className="text-sm font-medium w-24">Endpoint:</span>
                <code className="text-xs bg-muted px-2 py-1 rounded">
                  {scraperInfo.endpoint}
                </code>
              </div>

              {/* API Key Status */}
              {scraperInfo.type === 'firecrawl' && (
                <div className="flex items-center gap-4">
                  <span className="text-sm font-medium w-24">API Key:</span>
                  <Badge variant={scraperInfo.hasApiKey ? 'default' : 'destructive'}>
                    {scraperInfo.hasApiKey ? '✅ Configured' : '❌ Not Configured'}
                  </Badge>
                </div>
              )}

              {/* Description */}
              <Alert>
                <AlertDescription>
                  {scraperInfo.type === 'clawdbot' ? (
                    <>
                      <strong>Development Mode</strong>: Using local Clawdbot service (free testing)
                      <br />
                      Ensure Clawdbot is running: <code>./start-clawdbot.bat</code>
                    </>
                  ) : (
                    <>
                      <strong>Production Mode</strong>: Using cloud Firecrawl service (stable & reliable)
                      <br />
                      Ensure environment variable is configured: <code>FIRECRAWL_API_KEY</code>
                    </>
                  )}
                </AlertDescription>
              </Alert>
            </div>
          ) : (
            <p className="text-muted-foreground">Loading...</p>
          )}
        </CardContent>
      </Card>

      {/* Test Scraping */}
      <Card>
        <CardHeader>
          <CardTitle>Test Scraping</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="text-sm font-medium">Test URL</label>
            <Input
              value={testUrl}
              onChange={(e) => setTestUrl(e.target.value)}
              placeholder="https://www.hktvmall.com/..."
              className="mt-1"
            />
          </div>

          <Button
            onClick={handleTestScrape}
            disabled={loading || !scraperInfo || scraperInfo.status !== 'connected'}
            className="w-full"
          >
            {loading ? 'Scraping...' : 'Start Scraping'}
          </Button>

          {/* Scrape Result */}
          {result && (
            <div className="mt-6">
              <h3 className="text-lg font-semibold mb-2">Scrape Result</h3>
              <div className="bg-muted p-4 rounded-lg">
                {result.success ? (
                  <div className="space-y-2">
                    <Badge className="bg-green-500">✅ Scrape Successful</Badge>
                    <div className="text-sm text-muted-foreground">
                      <div>
                        <strong>Scraper:</strong> {result.metadata?.scraper}
                      </div>
                      <div>
                        <strong>Duration:</strong> {result.metadata?.durationMs}ms
                      </div>
                      <div>
                        <strong>Task ID:</strong> {result.metadata?.taskId}
                      </div>
                    </div>
                    <Textarea
                      value={JSON.stringify(result.data, null, 2)}
                      readOnly
                      rows={15}
                      className="mt-2 font-mono text-xs"
                    />
                  </div>
                ) : (
                  <div className="space-y-2">
                    <Badge variant="destructive">❌ Scrape Failed</Badge>
                    <p className="text-sm text-red-600">{result.error}</p>
                  </div>
                )}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Architecture Overview */}
      <Card>
        <CardHeader>
          <CardTitle>Hybrid Architecture Overview</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            {/* Development Environment */}
            <div className="border rounded-lg p-4">
              <h4 className="font-semibold mb-2 flex items-center gap-2">
                🤖 Development
              </h4>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>✅ Local Clawdbot</li>
                <li>✅ Free testing</li>
                <li>✅ Fully customizable</li>
                <li>✅ Rapid iteration</li>
              </ul>
              <code className="text-xs bg-muted px-2 py-1 rounded block mt-2">
                NODE_ENV=development
              </code>
            </div>

            {/* Production Environment */}
            <div className="border rounded-lg p-4">
              <h4 className="font-semibold mb-2 flex items-center gap-2">
                🔥 Production
              </h4>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>✅ Cloud Firecrawl</li>
                <li>✅ Stable & reliable</li>
                <li>✅ Auto-scaling</li>
                <li>✅ Professional support</li>
              </ul>
              <code className="text-xs bg-muted px-2 py-1 rounded block mt-2">
                NODE_ENV=production
              </code>
            </div>
          </div>

          <Alert>
            <AlertDescription>
              <strong>Auto-switching</strong>: The system automatically selects the appropriate scraper service based on the <code>NODE_ENV</code>{' '}
              environment variable — no manual configuration needed.
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    </div>
  );
}
