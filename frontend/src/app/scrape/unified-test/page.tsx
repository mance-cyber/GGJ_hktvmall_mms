'use client';

// ==================== 统一爬虫测试页面 ====================
// 用途: 测试混合架构的自动切换功能
// 路径: /scrape/unified-test

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

  // ==================== 获取爬虫配置信息 ====================

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
      console.error('获取爬虫信息失败:', error);
    }
  };

  // ==================== 测试抓取 ====================

  const handleTestScrape = async () => {
    if (!testUrl) {
      alert('请输入测试 URL');
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
        error: error instanceof Error ? error.message : '未知错误',
      });
    } finally {
      setLoading(false);
    }
  };

  // ==================== 渲染 ====================

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
      {/* 页面标题 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">统一爬虫测试</h1>
          <p className="text-muted-foreground mt-1">
            测试混合架构的自动切换功能
          </p>
        </div>
        <Button onClick={fetchScraperInfo} variant="outline">
          🔄 刷新状态
        </Button>
      </div>

      {/* 爬虫配置信息 */}
      <Card>
        <CardHeader>
          <CardTitle>当前爬虫配置</CardTitle>
        </CardHeader>
        <CardContent>
          {scraperInfo ? (
            <div className="space-y-4">
              {/* 爬虫类型 */}
              <div className="flex items-center gap-4">
                <span className="text-sm font-medium w-24">爬虫类型:</span>
                <Badge className={getScraperBadgeColor(scraperInfo.type)}>
                  {scraperInfo.type === 'clawdbot' ? '🤖 Clawdbot' : '🔥 Firecrawl'}
                </Badge>
              </div>

              {/* 环境 */}
              <div className="flex items-center gap-4">
                <span className="text-sm font-medium w-24">环境:</span>
                <Badge variant="outline">{scraperInfo.environment}</Badge>
              </div>

              {/* 连接状态 */}
              <div className="flex items-center gap-4">
                <span className="text-sm font-medium w-24">连接状态:</span>
                <div className="flex items-center gap-2">
                  <div
                    className={`h-3 w-3 rounded-full ${getStatusColor(
                      scraperInfo.status
                    )}`}
                  />
                  <span className="text-sm">
                    {scraperInfo.status === 'connected' ? '已连接' : '未连接'}
                  </span>
                </div>
              </div>

              {/* 端点 */}
              <div className="flex items-center gap-4">
                <span className="text-sm font-medium w-24">端点:</span>
                <code className="text-xs bg-muted px-2 py-1 rounded">
                  {scraperInfo.endpoint}
                </code>
              </div>

              {/* API Key 状态 */}
              {scraperInfo.type === 'firecrawl' && (
                <div className="flex items-center gap-4">
                  <span className="text-sm font-medium w-24">API Key:</span>
                  <Badge variant={scraperInfo.hasApiKey ? 'default' : 'destructive'}>
                    {scraperInfo.hasApiKey ? '✅ 已配置' : '❌ 未配置'}
                  </Badge>
                </div>
              )}

              {/* 说明 */}
              <Alert>
                <AlertDescription>
                  {scraperInfo.type === 'clawdbot' ? (
                    <>
                      <strong>开发模式</strong>: 使用本地 Clawdbot 服务 (免费测试)
                      <br />
                      确保 Clawdbot 已启动: <code>./start-clawdbot.bat</code>
                    </>
                  ) : (
                    <>
                      <strong>生产模式</strong>: 使用云端 Firecrawl 服务 (稳定可靠)
                      <br />
                      确保环境变量已配置: <code>FIRECRAWL_API_KEY</code>
                    </>
                  )}
                </AlertDescription>
              </Alert>
            </div>
          ) : (
            <p className="text-muted-foreground">加载中...</p>
          )}
        </CardContent>
      </Card>

      {/* 测试抓取 */}
      <Card>
        <CardHeader>
          <CardTitle>测试抓取</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="text-sm font-medium">测试 URL</label>
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
            {loading ? '抓取中...' : '开始抓取'}
          </Button>

          {/* 抓取结果 */}
          {result && (
            <div className="mt-6">
              <h3 className="text-lg font-semibold mb-2">抓取结果</h3>
              <div className="bg-muted p-4 rounded-lg">
                {result.success ? (
                  <div className="space-y-2">
                    <Badge className="bg-green-500">✅ 抓取成功</Badge>
                    <div className="text-sm text-muted-foreground">
                      <div>
                        <strong>爬虫:</strong> {result.metadata?.scraper}
                      </div>
                      <div>
                        <strong>耗时:</strong> {result.metadata?.durationMs}ms
                      </div>
                      <div>
                        <strong>任务 ID:</strong> {result.metadata?.taskId}
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
                    <Badge variant="destructive">❌ 抓取失败</Badge>
                    <p className="text-sm text-red-600">{result.error}</p>
                  </div>
                )}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* 架构说明 */}
      <Card>
        <CardHeader>
          <CardTitle>混合架构说明</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            {/* 开发环境 */}
            <div className="border rounded-lg p-4">
              <h4 className="font-semibold mb-2 flex items-center gap-2">
                🤖 开发环境
              </h4>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>✅ 使用本地 Clawdbot</li>
                <li>✅ 免费测试</li>
                <li>✅ 完全自定义</li>
                <li>✅ 快速迭代</li>
              </ul>
              <code className="text-xs bg-muted px-2 py-1 rounded block mt-2">
                NODE_ENV=development
              </code>
            </div>

            {/* 生产环境 */}
            <div className="border rounded-lg p-4">
              <h4 className="font-semibold mb-2 flex items-center gap-2">
                🔥 生产环境
              </h4>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>✅ 使用云端 Firecrawl</li>
                <li>✅ 稳定可靠</li>
                <li>✅ 自动扩展</li>
                <li>✅ 专业支持</li>
              </ul>
              <code className="text-xs bg-muted px-2 py-1 rounded block mt-2">
                NODE_ENV=production
              </code>
            </div>
          </div>

          <Alert>
            <AlertDescription>
              <strong>自动切换</strong>: 系统根据 <code>NODE_ENV</code>{' '}
              环境变量自动选择合适的爬虫服务，无需手动配置。
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    </div>
  );
}
