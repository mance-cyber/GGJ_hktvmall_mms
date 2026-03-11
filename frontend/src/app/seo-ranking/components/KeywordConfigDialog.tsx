"use client";

// =============================================
// Keyword Configuration Dialog Component
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

  // Form state
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

  // Initialize form
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
        // Update
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
        // Single create
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
        // Batch create
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
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Dialog */}
      <div className="relative bg-gray-900 border border-cyan-500/30 rounded-xl w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto">
        {/* Title */}
        <div className="flex items-center justify-between p-4 border-b border-gray-800">
          <h2 className="text-lg font-bold text-white">
            {isEditing ? "Edit Keyword" : "Add Keyword"}
          </h2>
          <button
            onClick={onClose}
            className="p-1 text-gray-400 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Mode Toggle (shown only when adding) */}
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
              Single Add
            </button>
            <button
              onClick={() => setMode("batch")}
              className={`flex-1 py-3 text-sm font-medium transition-colors ${
                mode === "batch"
                  ? "text-cyan-400 border-b-2 border-cyan-400"
                  : "text-gray-400 hover:text-white"
              }`}
            >
              Batch Add
            </button>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-4 space-y-4">
          {/* Single mode: keyword input */}
          {mode === "single" && (
            <div>
              <label className="block text-sm text-gray-400 mb-1">
                Keyword <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={formData.keyword}
                onChange={(e) =>
                  setFormData((prev) => ({ ...prev, keyword: e.target.value }))
                }
                disabled={isEditing}
                placeholder="Enter keyword"
                className="w-full bg-gray-800/50 border border-cyan-500/30 rounded-lg px-3 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 disabled:opacity-50"
                required={mode === "single"}
              />
            </div>
          )}

          {/* Batch mode: multi-line input */}
          {mode === "batch" && (
            <div>
              <label className="block text-sm text-gray-400 mb-1">
                Keyword List <span className="text-red-500">*</span>
              </label>
              <textarea
                value={batchKeywords}
                onChange={(e) => setBatchKeywords(e.target.value)}
                placeholder="Enter one keyword per line&#10;e.g.:&#10;日本零食&#10;進口糖果&#10;抹茶食品"
                rows={6}
                className="w-full bg-gray-800/50 border border-cyan-500/30 rounded-lg px-3 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 resize-none"
                required={mode === "batch"}
              />
              <p className="text-xs text-gray-500 mt-1">
                {batchKeywords.split("\n").filter((k) => k.trim()).length} keywords entered
              </p>
            </div>
          )}

          {/* Keyword Type */}
          <div>
            <label className="block text-sm text-gray-400 mb-1">Type</label>
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
              <option value="primary">Primary Keyword</option>
              <option value="secondary">Secondary Keyword</option>
              <option value="long_tail">Long-tail Keyword</option>
              <option value="brand">Brand Keyword</option>
              <option value="competitor">Competitor Keyword</option>
            </select>
          </div>

          {/* Tracking Options */}
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
              <span className="text-sm text-gray-300">Track Google</span>
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
              <span className="text-sm text-gray-300">Track HKTVmall</span>
            </label>
          </div>

          {/* Target Ranking (single mode only) */}
          {mode === "single" && (
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">
                  Google Target Rank
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
                  placeholder="e.g. 10"
                  className="w-full bg-gray-800/50 border border-cyan-500/30 rounded-lg px-3 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">
                  HKTVmall TargetRanking
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
                  placeholder="e.g. 5"
                  className="w-full bg-gray-800/50 border border-cyan-500/30 rounded-lg px-3 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500"
                />
              </div>
            </div>
          )}

          {/* Tags (single mode only) */}
          {mode === "single" && (
            <div>
              <label className="block text-sm text-gray-400 mb-1">Tags</label>
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
                  placeholder="Add tag"
                  className="flex-1 bg-gray-800/50 border border-cyan-500/30 rounded-lg px-3 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500"
                />
                <HoloButton type="button" variant="ghost" onClick={handleAddTag}>
                  <Plus className="w-4 h-4" />
                </HoloButton>
              </div>
            </div>
          )}

          {/* Notes (single mode only) */}
          {mode === "single" && (
            <div>
              <label className="block text-sm text-gray-400 mb-1">Notes</label>
              <textarea
                value={formData.notes}
                onChange={(e) =>
                  setFormData((prev) => ({ ...prev, notes: e.target.value }))
                }
                placeholder="Optional notes..."
                rows={2}
                className="w-full bg-gray-800/50 border border-cyan-500/30 rounded-lg px-3 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 resize-none"
              />
            </div>
          )}

          {/* button */}
          <div className="flex justify-end gap-3 pt-4 border-t border-gray-800">
            <HoloButton type="button" variant="ghost" onClick={onClose}>
              Cancel
            </HoloButton>
            <HoloButton type="submit" disabled={isPending}>
              {isPending
                ? "Processing..."
                : isEditing
                ? "Save"
                : mode === "batch"
                ? "Batch Add"
                : "Add"}
            </HoloButton>
          </div>
        </form>
      </div>
    </div>
  );
}
