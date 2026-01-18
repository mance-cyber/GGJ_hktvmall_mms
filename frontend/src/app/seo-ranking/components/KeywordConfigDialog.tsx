"use client";

// =============================================
// 關鍵詞配置對話框組件
// =============================================

import { useState, useEffect } from "react";
import { X, Plus, Trash2 } from "lucide-react";
import { HoloButton } from "@/components/ui/future-tech";
import {
  useCreateKeywordConfig,
  useUpdateKeywordConfig,
  useBatchCreateKeywordConfigs,
} from "../hooks/useSEORanking";
import { KeywordConfig, KeywordType } from "@/lib/api/seo-ranking";

interface KeywordConfigDialogProps {
  isOpen: boolean;
  onClose: () => void;
  keyword?: KeywordConfig | null;
}

export function KeywordConfigDialog({
  isOpen,
  onClose,
  keyword,
}: KeywordConfigDialogProps) {
  const isEditing = !!keyword;

  // 表單狀態
  const [mode, setMode] = useState<"single" | "batch">("single");
  const [formData, setFormData] = useState({
    keyword: "",
    keyword_type: "primary" as KeywordType,
    track_google: true,
    track_hktvmall: true,
    target_google_rank: "",
    target_hktvmall_rank: "",
    notes: "",
    tags: [] as string[],
  });
  const [batchKeywords, setBatchKeywords] = useState("");
  const [newTag, setNewTag] = useState("");

  // API mutations
  const createKeyword = useCreateKeywordConfig();
  const updateKeyword = useUpdateKeywordConfig();
  const batchCreate = useBatchCreateKeywordConfigs();

  // 初始化表單
  useEffect(() => {
    if (keyword) {
      setFormData({
        keyword: keyword.keyword,
        keyword_type: keyword.keyword_type,
        track_google: keyword.track_google,
        track_hktvmall: keyword.track_hktvmall,
        target_google_rank: keyword.target_google_rank?.toString() || "",
        target_hktvmall_rank: keyword.target_hktvmall_rank?.toString() || "",
        notes: keyword.notes || "",
        tags: keyword.tags || [],
      });
      setMode("single");
    } else {
      setFormData({
        keyword: "",
        keyword_type: "primary",
        track_google: true,
        track_hktvmall: true,
        target_google_rank: "",
        target_hktvmall_rank: "",
        notes: "",
        tags: [],
      });
      setBatchKeywords("");
    }
  }, [keyword, isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      if (isEditing) {
        // 更新
        await updateKeyword.mutateAsync({
          id: keyword.id,
          data: {
            keyword_type: formData.keyword_type,
            track_google: formData.track_google,
            track_hktvmall: formData.track_hktvmall,
            target_google_rank: formData.target_google_rank
              ? parseInt(formData.target_google_rank)
              : null,
            target_hktvmall_rank: formData.target_hktvmall_rank
              ? parseInt(formData.target_hktvmall_rank)
              : null,
            notes: formData.notes || undefined,
            tags: formData.tags.length > 0 ? formData.tags : undefined,
          },
        });
      } else if (mode === "single") {
        // 單個創建
        await createKeyword.mutateAsync({
          keyword: formData.keyword,
          keyword_type: formData.keyword_type,
          track_google: formData.track_google,
          track_hktvmall: formData.track_hktvmall,
          target_google_rank: formData.target_google_rank
            ? parseInt(formData.target_google_rank)
            : undefined,
          target_hktvmall_rank: formData.target_hktvmall_rank
            ? parseInt(formData.target_hktvmall_rank)
            : undefined,
          notes: formData.notes || undefined,
          tags: formData.tags.length > 0 ? formData.tags : undefined,
        });
      } else {
        // 批量創建
        const keywords = batchKeywords
          .split("\n")
          .map((k) => k.trim())
          .filter((k) => k.length > 0);
        if (keywords.length === 0) return;

        await batchCreate.mutateAsync({
          keywords,
          keyword_type: formData.keyword_type,
          track_google: formData.track_google,
          track_hktvmall: formData.track_hktvmall,
        });
      }
      onClose();
    } catch (error) {
      console.error("Failed to save keyword:", error);
    }
  };

  const handleAddTag = () => {
    if (newTag && !formData.tags.includes(newTag)) {
      setFormData((prev) => ({
        ...prev,
        tags: [...prev.tags, newTag],
      }));
      setNewTag("");
    }
  };

  const handleRemoveTag = (tag: string) => {
    setFormData((prev) => ({
      ...prev,
      tags: prev.tags.filter((t) => t !== tag),
    }));
  };

  const isPending =
    createKeyword.isPending || updateKeyword.isPending || batchCreate.isPending;

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* 背景遮罩 */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* 對話框 */}
      <div className="relative bg-gray-900 border border-cyan-500/30 rounded-xl w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto">
        {/* 標題 */}
        <div className="flex items-center justify-between p-4 border-b border-gray-800">
          <h2 className="text-lg font-bold text-white">
            {isEditing ? "編輯關鍵詞" : "新增關鍵詞"}
          </h2>
          <button
            onClick={onClose}
            className="p-1 text-gray-400 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* 模式切換（僅新增時顯示） */}
        {!isEditing && (
          <div className="flex border-b border-gray-800">
            <button
              onClick={() => setMode("single")}
              className={`flex-1 py-3 text-sm font-medium transition-colors ${
                mode === "single"
                  ? "text-cyan-400 border-b-2 border-cyan-400"
                  : "text-gray-400 hover:text-white"
              }`}
            >
              單個新增
            </button>
            <button
              onClick={() => setMode("batch")}
              className={`flex-1 py-3 text-sm font-medium transition-colors ${
                mode === "batch"
                  ? "text-cyan-400 border-b-2 border-cyan-400"
                  : "text-gray-400 hover:text-white"
              }`}
            >
              批量新增
            </button>
          </div>
        )}

        {/* 表單 */}
        <form onSubmit={handleSubmit} className="p-4 space-y-4">
          {/* 單個模式：關鍵詞輸入 */}
          {mode === "single" && (
            <div>
              <label className="block text-sm text-gray-400 mb-1">
                關鍵詞 <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={formData.keyword}
                onChange={(e) =>
                  setFormData((prev) => ({ ...prev, keyword: e.target.value }))
                }
                disabled={isEditing}
                placeholder="輸入關鍵詞"
                className="w-full bg-gray-800/50 border border-cyan-500/30 rounded-lg px-3 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 disabled:opacity-50"
                required={mode === "single"}
              />
            </div>
          )}

          {/* 批量模式：多行輸入 */}
          {mode === "batch" && (
            <div>
              <label className="block text-sm text-gray-400 mb-1">
                關鍵詞列表 <span className="text-red-500">*</span>
              </label>
              <textarea
                value={batchKeywords}
                onChange={(e) => setBatchKeywords(e.target.value)}
                placeholder="每行輸入一個關鍵詞&#10;例如：&#10;日本零食&#10;進口糖果&#10;抹茶食品"
                rows={6}
                className="w-full bg-gray-800/50 border border-cyan-500/30 rounded-lg px-3 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 resize-none"
                required={mode === "batch"}
              />
              <p className="text-xs text-gray-500 mt-1">
                已輸入{" "}
                {batchKeywords.split("\n").filter((k) => k.trim()).length} 個關鍵詞
              </p>
            </div>
          )}

          {/* 關鍵詞類型 */}
          <div>
            <label className="block text-sm text-gray-400 mb-1">類型</label>
            <select
              value={formData.keyword_type}
              onChange={(e) =>
                setFormData((prev) => ({
                  ...prev,
                  keyword_type: e.target.value as KeywordType,
                }))
              }
              className="w-full bg-gray-800/50 border border-cyan-500/30 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-cyan-500"
            >
              <option value="primary">主要關鍵詞</option>
              <option value="secondary">次要關鍵詞</option>
              <option value="long_tail">長尾關鍵詞</option>
              <option value="brand">品牌關鍵詞</option>
              <option value="competitor">競品關鍵詞</option>
            </select>
          </div>

          {/* 追蹤選項 */}
          <div className="grid grid-cols-2 gap-4">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={formData.track_google}
                onChange={(e) =>
                  setFormData((prev) => ({
                    ...prev,
                    track_google: e.target.checked,
                  }))
                }
                className="w-4 h-4 rounded border-gray-600 bg-gray-800 text-cyan-500 focus:ring-cyan-500"
              />
              <span className="text-sm text-gray-300">追蹤 Google</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={formData.track_hktvmall}
                onChange={(e) =>
                  setFormData((prev) => ({
                    ...prev,
                    track_hktvmall: e.target.checked,
                  }))
                }
                className="w-4 h-4 rounded border-gray-600 bg-gray-800 text-cyan-500 focus:ring-cyan-500"
              />
              <span className="text-sm text-gray-300">追蹤 HKTVmall</span>
            </label>
          </div>

          {/* 目標排名（僅單個模式） */}
          {mode === "single" && (
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">
                  Google 目標排名
                </label>
                <input
                  type="number"
                  min="1"
                  max="100"
                  value={formData.target_google_rank}
                  onChange={(e) =>
                    setFormData((prev) => ({
                      ...prev,
                      target_google_rank: e.target.value,
                    }))
                  }
                  placeholder="例如: 10"
                  className="w-full bg-gray-800/50 border border-cyan-500/30 rounded-lg px-3 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">
                  HKTVmall 目標排名
                </label>
                <input
                  type="number"
                  min="1"
                  max="100"
                  value={formData.target_hktvmall_rank}
                  onChange={(e) =>
                    setFormData((prev) => ({
                      ...prev,
                      target_hktvmall_rank: e.target.value,
                    }))
                  }
                  placeholder="例如: 5"
                  className="w-full bg-gray-800/50 border border-cyan-500/30 rounded-lg px-3 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500"
                />
              </div>
            </div>
          )}

          {/* 標籤（僅單個模式） */}
          {mode === "single" && (
            <div>
              <label className="block text-sm text-gray-400 mb-1">標籤</label>
              <div className="flex gap-2 mb-2 flex-wrap">
                {formData.tags.map((tag) => (
                  <span
                    key={tag}
                    className="inline-flex items-center gap-1 px-2 py-1 rounded bg-cyan-500/20 text-cyan-400 text-sm"
                  >
                    {tag}
                    <button
                      type="button"
                      onClick={() => handleRemoveTag(tag)}
                      className="hover:text-red-400"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </span>
                ))}
              </div>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={newTag}
                  onChange={(e) => setNewTag(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      e.preventDefault();
                      handleAddTag();
                    }
                  }}
                  placeholder="新增標籤"
                  className="flex-1 bg-gray-800/50 border border-cyan-500/30 rounded-lg px-3 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500"
                />
                <HoloButton type="button" variant="ghost" onClick={handleAddTag}>
                  <Plus className="w-4 h-4" />
                </HoloButton>
              </div>
            </div>
          )}

          {/* 備註（僅單個模式） */}
          {mode === "single" && (
            <div>
              <label className="block text-sm text-gray-400 mb-1">備註</label>
              <textarea
                value={formData.notes}
                onChange={(e) =>
                  setFormData((prev) => ({ ...prev, notes: e.target.value }))
                }
                placeholder="可選備註..."
                rows={2}
                className="w-full bg-gray-800/50 border border-cyan-500/30 rounded-lg px-3 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 resize-none"
              />
            </div>
          )}

          {/* 按鈕 */}
          <div className="flex justify-end gap-3 pt-4 border-t border-gray-800">
            <HoloButton type="button" variant="ghost" onClick={onClose}>
              取消
            </HoloButton>
            <HoloButton type="submit" disabled={isPending}>
              {isPending
                ? "處理中..."
                : isEditing
                ? "儲存"
                : mode === "batch"
                ? "批量新增"
                : "新增"}
            </HoloButton>
          </div>
        </form>
      </div>
    </div>
  );
}
