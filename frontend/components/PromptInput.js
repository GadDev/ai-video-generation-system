'use client';

import { useState } from 'react';

export default function PromptInput({ onPromptChange, disabled }) {
  const [prompt, setPrompt] = useState('');
  const MAX_LENGTH = 500;

  const handleChange = (e) => {
    const value = e.target.value;
    if (value.length <= MAX_LENGTH) {
      setPrompt(value);
      onPromptChange(value);
    }
  };

  return (
    <div className="w-full">
      <label className="block text-sm font-semibold text-gray-200 mb-2">
        Generation Prompt
      </label>

      <textarea
        value={prompt}
        onChange={handleChange}
        disabled={disabled}
        placeholder="e.g., anime cyberpunk rooftop at sunset, cinematic camera movement"
        className="w-full h-24 p-3 border border-gray-400 rounded-lg bg-gray-800 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
      />

      <div className="flex justify-between items-center mt-2">
        <p className="text-xs text-gray-400">
          {prompt.length}/{MAX_LENGTH} characters
        </p>
        {prompt.length === MAX_LENGTH && (
          <p className="text-xs text-yellow-400">Max length reached</p>
        )}
      </div>
    </div>
  );
}
