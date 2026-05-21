'use client';

import { useState } from 'react';

export default function ImageUpload({ onImagesSelected, disabled }) {
  const [images, setImages] = useState([]);

  const handleDragOver = (e) => {
    e.preventDefault();
    e.currentTarget.classList.add('border-blue-500', 'bg-blue-50');
  };

  const handleDragLeave = (e) => {
    e.currentTarget.classList.remove('border-blue-500', 'bg-blue-50');
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.currentTarget.classList.remove('border-blue-500', 'bg-blue-50');
    const files = Array.from(e.dataTransfer.files);
    addImages(files);
  };

  const handleFileInput = (e) => {
    const files = Array.from(e.target.files || []);
    addImages(files);
  };

  const addImages = (files) => {
    const imageFiles = files.filter((f) => f.type.startsWith('image/'));
    const validFiles = imageFiles.filter((f) => f.size < 10 * 1024 * 1024);

    if (validFiles.length !== imageFiles.length) {
      alert('Some files exceeded 10MB limit and were skipped');
    }

    if (validFiles.length + images.length > 5) {
      alert('Maximum 5 images allowed');
      return;
    }

    const newImages = validFiles.map((file) => ({
      id: Math.random(),
      file,
      preview: URL.createObjectURL(file),
    }));

    setImages([...images, ...newImages]);
    onImagesSelected([...images, ...newImages]);
  };

  const removeImage = (id) => {
    const updated = images.filter((img) => img.id !== id);
    setImages(updated);
    onImagesSelected(updated);
  };

  return (
    <div className="w-full">
      <label className="block text-sm font-semibold text-gray-200 mb-2">
        Upload Images (Optional, 0-5)
      </label>

      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className="border-2 border-dashed border-gray-400 rounded-lg p-8 text-center cursor-pointer hover:border-blue-400 transition"
      >
        <input
          type="file"
          multiple
          accept="image/*"
          onChange={handleFileInput}
          disabled={disabled}
          className="hidden"
          id="file-input"
        />
        <label htmlFor="file-input" className="cursor-pointer">
          <p className="text-gray-300">Drag images here or click to select</p>
          <p className="text-sm text-gray-400 mt-1">JPEG, PNG up to 10MB each</p>
        </label>
      </div>

      {images.length > 0 && (
        <div className="mt-4 grid grid-cols-3 gap-3">
          {images.map((img) => (
            <div key={img.id} className="relative">
              <img
                src={img.preview}
                alt="preview"
                className="w-full h-24 object-cover rounded-lg"
              />
              <button
                onClick={() => removeImage(img.id)}
                className="absolute top-1 right-1 bg-red-500 text-white text-xs px-2 py-1 rounded"
              >
                Remove
              </button>
            </div>
          ))}
        </div>
      )}

      <p className="text-xs text-gray-400 mt-2">
        Selected: {images.length}/5
      </p>
    </div>
  );
}
