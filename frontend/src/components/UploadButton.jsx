import React, { useRef, useState } from 'react';
import { Upload, FileCheck, Loader2 } from 'lucide-react';
import { uploadDocument } from '../hooks/api.js';

export default function UploadButton({ onUpload }) {
  const inputRef = useRef(null);
  const [uploading, setUploading] = useState(false);
  const [lastResult, setLastResult] = useState(null);

  const handleFile = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setLastResult(null);
    try {
      const result = await uploadDocument(file);
      setLastResult(result);
      onUpload?.(result);
    } catch (err) {
      setLastResult({ error: err.message });
    } finally {
      setUploading(false);
      if (inputRef.current) inputRef.current.value = '';
    }
  };

  return (
    <div className="relative">
      <input
        ref={inputRef}
        type="file"
        accept=".pdf"
        onChange={handleFile}
        className="hidden"
      />
      <button
        onClick={() => inputRef.current?.click()}
        disabled={uploading}
        className="flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-medium bg-surface-2 border border-surface-3 text-gray-400 hover:text-accent-glow hover:border-accent/30 transition-all disabled:opacity-50"
      >
        {uploading ? (
          <Loader2 size={14} className="animate-spin" />
        ) : lastResult?.chunks_created ? (
          <FileCheck size={14} className="text-success" />
        ) : (
          <Upload size={14} />
        )}
        {uploading
          ? 'Processing...'
          : lastResult?.chunks_created
          ? `${lastResult.chunks_created} chunks`
          : 'Upload PDF'}
      </button>
    </div>
  );
}
