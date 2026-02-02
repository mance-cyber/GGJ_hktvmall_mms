# 將 HTML 轉換為 Word 文檔
$htmlPath = "E:\Mance\Mercury\Project\7. App dev\4. GoGoJap - HKTVmall AI system\docs\GoGoJap-投資者成本分析.html"
$docxPath = "E:\Mance\Mercury\Project\7. App dev\4. GoGoJap - HKTVmall AI system\docs\GoGoJap-投資者成本分析.docx"

Write-Host "正在轉換 HTML 到 Word..."

$word = New-Object -ComObject Word.Application
$word.Visible = $false

$doc = $word.Documents.Open($htmlPath)
$doc.SaveAs([ref]$docxPath, [ref]16)  # 16 = wdFormatDocumentDefault (.docx)
$doc.Close()
$word.Quit()

[System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null
[System.GC]::Collect()
[System.GC]::WaitForPendingFinalizers()

Write-Host "✅ 轉換完成！"
Write-Host "Word 文檔已保存至: $docxPath"
