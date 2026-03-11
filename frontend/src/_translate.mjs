// Bulk Chinese → English translation script for GoGoJap frontend
// Only translates UI text and comments, preserves variable names and logic

import { readFileSync, writeFileSync } from 'fs';
import { execSync } from 'child_process';
import { resolve } from 'path';

// Get all files with Chinese characters
const srcDir = resolve('.');
const files = execSync(
  `powershell -Command "Get-ChildItem -Recurse -Include *.tsx,*.ts,*.jsx | Select-String -Pattern '[\\u4e00-\\u9fff]' | Select-Object -ExpandProperty Path -Unique"`,
  { cwd: srcDir, encoding: 'utf-8' }
).trim().split('\n').map(f => f.trim()).filter(f => f && !f.startsWith('Active code page') && f.endsWith('.tsx') || f.endsWith('.ts') || f.endsWith('.jsx'));

console.log(`Found ${files.length} files with Chinese text\n`);

// Translation dictionary - ordered from longest to shortest to avoid partial matches
const translations = [
  // === Common comment patterns ===
  // Image generation
  ['圖片生成上傳頁面', 'Image Generation Upload Page'],
  ['圖片生成歷史記錄頁面', 'Image Generation History Page'],
  ['圖片生成結果頁面', 'Image Generation Results Page'],
  ['圖片上傳區域', 'Image upload area'],
  ['圖片信息和分析結果', 'Image info and analysis results'],
  ['圖片預覽', 'Image preview'],
  ['輸入圖片和 AI 分析結果', 'Input images and AI analysis results'],
  ['輸出圖片', 'Output images'],
  ['每張圖片輸出數量', 'Outputs per image'],
  
  // Status/state
  ['狀態標籤組件', 'Status Badge Component'],
  ['狀態指示器', 'Status indicator'],
  ['分析中狀態', 'Analyzing state'],
  ['處理中提示', 'Processing hint'],
  ['加載狀態', 'Loading state'],
  ['錯誤狀態', 'Error state'],
  ['空狀態', 'Empty state'],
  
  // Operations  
  ['選中的任務（用於批量刪除）', 'Selected tasks (for batch deletion)'],
  ['選中/取消選中單個任務', 'Select / Deselect individual task'],
  ['全選/取消全選', 'Select all / Deselect all'],
  ['批量刪除任務', 'Batch delete tasks'],
  ['批量操作欄', 'Batch operation bar'],
  ['刪除單個任務', 'Delete single task'],
  ['查看任務詳情', 'View task details'],
  ['加載任務列表', 'Load task list'],
  
  // UI structure
  ['格式化日期', 'Format date'],
  ['計算剩餘天數', 'Calculate remaining days'],
  ['計算總頁數', 'Calculate total pages'],
  ['根據角色計算限制', 'Calculate limits based on role'],
  
  // Steps
  ['跳轉到結果頁面', 'Redirect to results page'],
  ['開始生成', 'Start generation'],
  ['上傳圖片', 'Upload images'],
  ['創建任務', 'Create task'],
  
  // Mode descriptions
  ['生成模式選擇', 'Generation mode selection'],
  ['白底圖模式', 'White background mode'],
  ['專業攝影模式', 'Professional photo mode'],
  ['風格描述（專業攝影模式才顯示）', 'Style description (shown for professional photo mode only)'],
  
  // AI Analysis
  ['AI 分析結果摘要', 'AI analysis result summary'],
  ['展開/收起 Prompt', 'Expand/Collapse Prompt'],
  ['產品類型', 'Product type'],
  ['視覺描述', 'Visual description'],
  
  // Common JSX comments
  ['錯誤訊息', 'Error message'],
  ['提交按鈕', 'Submit button'],
  ['標題', 'Title'],
  ['分頁', 'Pagination'],
  ['進度條', 'Progress bar'],
  ['搜尋', 'Search'],
  ['篩選', 'Filter'],
  ['排序', 'Sort'],
  ['操作', 'Actions'],
  ['內容', 'Content'],
  ['設定', 'Settings'],
  ['詳情', 'Details'],
  ['統計', 'Statistics'],
  ['摘要', 'Summary'],
  ['列表', 'List'],
  ['表格', 'Table'],
  ['卡片', 'Card'],
  ['對話框', 'Dialog'],
  ['彈窗', 'Popup'],
  ['側邊欄', 'Sidebar'],
  ['導航', 'Navigation'],
  ['頁腳', 'Footer'],
  ['頁首', 'Header'],
  ['麵包屑', 'Breadcrumb'],
  ['圖表', 'Chart'],
  ['圖示', 'Icon'],
  
  // Agent related
  ['排程編輯器組件', 'Schedule Editor Component'],
  ['排程面板組件', 'Schedule Panel Component'],
  ['排程編輯器', 'Schedule Editor'],
  ['排程面板', 'Schedule Panel'],
  ['對話列表', 'Conversation List'],
  ['快速操作', 'Quick Actions'],
  ['代理團隊', 'Agent Team'],
  ['代理頁面', 'Agent Page'],
  ['代理設定', 'Agent Settings'],
  
  // Pricing / Business
  ['定價審批', 'Pricing Approval'],
  ['價格建議', 'Pricing Suggestions'],
  ['價格歷史', 'Price History'],
  ['價格趨勢', 'Price Trends'],
  ['價格數據', 'Price Data'],
  ['定價影響', 'Pricing Impact'],
  ['投資回報', 'ROI'],
  ['投資回報率', 'Return on Investment'],
  ['競品分析', 'Competitor Analysis'],
  ['競品監測', 'Competitor Monitoring'],
  ['競品配對', 'Competitor Matching'],
  ['競品價值', 'Competitor Value'],
  ['市場回應', 'Market Response'],
  ['商品管理', 'Product Management'],
  ['商品分類', 'Product Categories'],
  ['批量導入', 'Bulk Import'],
  ['批量匹配', 'Batch Match'],
  ['批量生成', 'Batch Generation'],
  ['內容管線', 'Content Pipeline'],
  ['內容歷史', 'Content History'],
  ['內容優化', 'Content Optimization'],
  ['SEO 排名', 'SEO Ranking'],
  ['關鍵詞', 'Keywords'],
  ['排行榜', 'Leaderboard'],
  ['抓取任務', 'Scrape Tasks'],
  ['抓取', 'Scraping'],
  
  // Common UI text (hardcoded strings)
  ['正在加載', 'Loading'],
  ['加載中', 'Loading'],
  ['載入中', 'Loading'],
  ['暫無數據', 'No data available'],
  ['沒有數據', 'No data'],
  ['無資料', 'No data'],
  ['確定要刪除嗎？', 'Are you sure you want to delete?'],
  ['確定刪除？', 'Confirm deletion?'],
  ['刪除成功', 'Deleted successfully'],
  ['保存成功', 'Saved successfully'],
  ['操作成功', 'Operation successful'],
  ['操作失敗', 'Operation failed'],
  ['提交成功', 'Submitted successfully'],
  ['請選擇', 'Please select'],
  ['請輸入', 'Please enter'],
  ['請填寫', 'Please fill in'],
  ['取消', 'Cancel'],
  ['確定', 'Confirm'],
  ['確認', 'Confirm'],
  ['關閉', 'Close'],
  ['保存', 'Save'],
  ['刪除', 'Delete'],
  ['編輯', 'Edit'],
  ['新增', 'Add'],
  ['添加', 'Add'],
  ['搜索', 'Search'],
  ['重試', 'Retry'],
  ['返回', 'Back'],
  ['提交', 'Submit'],
  ['更新', 'Update'],
  ['上傳', 'Upload'],
  ['下載', 'Download'],
  ['導出', 'Export'],
  ['導入', 'Import'],
  ['全部', 'All'],
  ['已選擇', 'Selected'],
  ['未選擇', 'Not selected'],
  ['已完成', 'Completed'],
  ['進行中', 'In progress'],
  ['待處理', 'Pending'],
  ['已失敗', 'Failed'],
  ['已取消', 'Cancelled'],
  ['暫停', 'Paused'],
  ['啟用', 'Enable'],
  ['停用', 'Disable'],
  ['是', 'Yes'],
  ['否', 'No'],
  ['天', 'days'],
  ['小時', 'hours'],
  ['分鐘', 'minutes'],
  ['秒', 'seconds'],
  ['共', 'Total'],
  ['項', 'items'],
  ['條', 'items'],
  ['個', ''],
  ['張', ''],
  ['頁', 'page'],
  ['第', 'Page'],
];

let totalChanges = 0;
const changedFiles = [];

for (const filePath of files) {
  // Skip the zh-HK locale file (intentionally Chinese)
  if (filePath.includes('zh-HK')) {
    console.log(`⏭️  SKIP (locale file): ${filePath}`);
    continue;
  }
  // Skip this script
  if (filePath.includes('_translate')) continue;
  
  let content = readFileSync(filePath, 'utf-8');
  const original = content;
  
  // Apply translations
  for (const [cn, en] of translations) {
    content = content.replaceAll(cn, en);
  }
  
  if (content !== original) {
    writeFileSync(filePath, content, 'utf-8');
    totalChanges++;
    changedFiles.push(filePath.replace(srcDir, ''));
    console.log(`✅ ${filePath}`);
  }
}

console.log(`\n========================================`);
console.log(`Changed ${totalChanges} files`);
console.log(`========================================\n`);

// Now check what Chinese remains
const remaining = execSync(
  `powershell -Command "Get-ChildItem -Recurse -Include *.tsx,*.ts,*.jsx | Where-Object { $_.FullName -notmatch 'zh-HK' -and $_.FullName -notmatch '_translate' } | Select-String -Pattern '[\\u4e00-\\u9fff]' | Select-Object -ExpandProperty Path -Unique | Sort-Object"`,
  { cwd: srcDir, encoding: 'utf-8' }
).trim().split('\n').filter(f => f.trim() && !f.includes('Active code page')).join('\n');

if (remaining) {
  console.log(`Files still containing Chinese:\n${remaining}`);
} else {
  console.log('🎉 All Chinese text has been translated!');
}
