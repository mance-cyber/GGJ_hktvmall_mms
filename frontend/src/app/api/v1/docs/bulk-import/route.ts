// ==================== 批量导入文档 API ====================
// 端点: POST /api/v1/docs/bulk-import
// 用途: 接收本地抓取的数据，批量导入到云端数据库

import { NextRequest, NextResponse } from 'next/server';
// import { db } from '@/lib/db'; // 你的数据库客户端

// ==================== API Handler ====================

export async function POST(request: NextRequest) {
  try {
    // 验证 API Key (可选但推荐)
    const authHeader = request.headers.get('Authorization');
    const apiKey = authHeader?.replace('Bearer ', '');

    if (!apiKey || apiKey !== process.env.CLOUD_API_KEY) {
      return NextResponse.json(
        { success: false, error: '未授权' },
        { status: 401 }
      );
    }

    // Parse请求数据
    const body = await request.json();
    const { docs } = body;

    if (!docs || !Array.isArray(docs)) {
      return NextResponse.json(
        { success: false, error: 'docs 必须是数组' },
        { status: 400 }
      );
    }

    console.log(`📥 接收批量导入请求: ${docs.length} 条文档`);

    // 批量插入数据库
    const results = await bulkInsertDocs(docs);

    return NextResponse.json({
      success: true,
      imported: results.successCount,
      failed: results.failCount,
      total: docs.length,
    });
  } catch (error) {
    console.error('❌ 批量导入失败:', error);
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown错误',
      },
      { status: 500 }
    );
  }
}

// ==================== 数据库Operation ====================

/**
 * 批量插入文档到数据库
 */
async function bulkInsertDocs(docs: any[]) {
  let successCount = 0;
  let failCount = 0;

  // TODO: 替换为你的实际数据库Operation
  // 示例使用 Prisma:
  /*
  for (const doc of docs) {
    try {
      await db.clawdbotDocs.upsert({
        where: { url: doc.url },
        update: {
          title: doc.data?.title,
          content: doc.data?.content,
          html: doc.data?.html,
          markdown: doc.data?.markdown,
          scrapedAt: new Date(doc.scrapedAt),
        },
        create: {
          url: doc.url,
          title: doc.data?.title,
          content: doc.data?.content,
          html: doc.data?.html,
          markdown: doc.data?.markdown,
          scrapedAt: new Date(doc.scrapedAt),
        },
      });
      successCount++;
    } catch (error) {
      console.error(`插入失败: ${doc.url}`, error);
      failCount++;
    }
  }
  */

  // 临时实现：仅记录日志
  for (const doc of docs) {
    if (doc.success && doc.data) {
      console.log(`  ✓ ${doc.url}`);
      successCount++;
    } else {
      console.log(`  ✗ ${doc.url}`);
      failCount++;
    }
  }

  return { successCount, failCount };
}

// ==================== GET: 查询已导入的文档 ====================

export async function GET(request: NextRequest) {
  try {
    // 验证 API Key
    const authHeader = request.headers.get('Authorization');
    const apiKey = authHeader?.replace('Bearer ', '');

    if (!apiKey || apiKey !== process.env.CLOUD_API_KEY) {
      return NextResponse.json(
        { success: false, error: '未授权' },
        { status: 401 }
      );
    }

    // TODO: 查询数据库
    /*
    const docs = await db.clawdbotDocs.findMany({
      orderBy: { scrapedAt: 'desc' },
      take: 100,
    });
    */

    return NextResponse.json({
      success: true,
      total: 0, // docs.length
      docs: [], // docs
    });
  } catch (error) {
    console.error('❌ 查询文档失败:', error);
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown错误',
      },
      { status: 500 }
    );
  }
}
