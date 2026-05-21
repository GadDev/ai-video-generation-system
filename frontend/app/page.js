'use client';

import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import ImageUpload from '@/components/ImageUpload';
import PromptInput from '@/components/PromptInput';
import GenerationProgress from '@/components/GenerationProgress';
import VideoPreview from '@/components/VideoPreview';

export default function Home() {
  const [images, setImages] = useState([]);
  const [prompt, setPrompt] = useState('');
  const [jobId, setJobId] = useState(null);
  const [status, setStatus] = useState('idle');
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const pollIntervalRef = useRef(null);

  useEffect(() => {
    if (status === 'generating' && jobId) {
      pollStatus();
      pollIntervalRef.current = setInterval(pollStatus, 2000);

      return () => {
        if (pollIntervalRef.current) {
          clearInterval(pollIntervalRef.current);
        }
      };
    }
  }, [status, jobId]);

  const pollStatus = async () => {
    try {
      // Call backend directly instead of through Next.js proxy
      // (avoids proxy connection timeout issues during long generation)
      const response = await axios.get(`http://localhost:8000/status/${jobId}`, {
        timeout: 30000, // 30 second timeout for each poll
      });
      const data = response.data;

      setProgress(data.progress || 0);
      setMessage(data.message || '');

      if (data.status === 'complete') {
        setStatus('complete');
        setProgress(100);
        if (pollIntervalRef.current) {
          clearInterval(pollIntervalRef.current);
        }
      } else if (data.status === 'failed' || data.status === 'cancelled') {
        setStatus(data.status);
        setError(data.message || 'Generation failed');
        if (pollIntervalRef.current) {
          clearInterval(pollIntervalRef.current);
        }
      }
    } catch (err) {
      // Network errors during polling - don't stop polling, just log
      console.warn('Status poll temporary failure (will retry):', err.message);
      // Keep polling - backend might still be working
    }
  };

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      setError('Please enter a prompt');
      return;
    }

    setError('');

    const formData = new FormData();
    formData.append('prompt', prompt);
    images.forEach((img) => {
      formData.append('images', img.file);
    });

    try {
      setStatus('generating');
      setProgress(5);
      setMessage('Submitting generation request...');

      // Call backend directly instead of through Next.js proxy
      const response = await axios.post('http://localhost:8000/generate', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 60000, // 60 seconds to submit request
      });

      setJobId(response.data.job_id);
    } catch (err) {
      setStatus('error');
      setError(err.response?.data?.error || 'Failed to start generation');
    }
  };

  const handleCancel = async () => {
    if (!jobId) return;

    try {
      // Call backend directly instead of through Next.js proxy
      await axios.delete(`http://localhost:8000/generate/${jobId}`);
      setStatus('cancelled');
      setMessage('Generation cancelled');
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
    } catch (err) {
      setError('Failed to cancel generation');
      console.error('Cancel error:', err);
    }
  };

  const handleReset = () => {
    setImages([]);
    setPrompt('');
    setJobId(null);
    setStatus('idle');
    setProgress(0);
    setMessage('');
    setError('');
  };

  const isGenerating = status === 'generating';
  const isComplete = status === 'complete';
  const isError = status === 'error';

  return (
    <main className="min-h-screen bg-gradient-to-br from-purple-900 via-indigo-900 to-blue-900 p-8">
      <div className="max-w-2xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-white mb-2">
            🎬 AI Video Generator
          </h1>
          <p className="text-gray-300">
            Generate stunning anime video clips with AI
          </p>
        </div>

        {isComplete ? (
          <VideoPreview jobId={jobId} onReset={handleReset} />
        ) : (
          <div className="space-y-6">
            <div className="bg-gray-900 border border-gray-700 rounded-lg p-6">
              <ImageUpload
                onImagesSelected={setImages}
                disabled={isGenerating}
              />

              <div className="mt-6 pt-6 border-t border-gray-700">
                <PromptInput
                  onPromptChange={setPrompt}
                  disabled={isGenerating}
                />
              </div>

              {error && (
                <div className="mt-4 p-4 bg-red-900 border border-red-700 rounded-lg">
                  <p className="text-red-200 text-sm">{error}</p>
                </div>
              )}

              <button
                onClick={handleGenerate}
                disabled={isGenerating || !prompt.trim()}
                className="w-full mt-6 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold py-3 px-6 rounded-lg transition"
              >
                {isGenerating ? 'Generating...' : 'Generate Video'}
              </button>
            </div>

            {isGenerating && (
              <div>
                <GenerationProgress
                  status={status}
                  progress={progress}
                  message={message}
                />
                <button
                  onClick={handleCancel}
                  className="w-full mt-4 bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded-lg transition"
                >
                  Cancel Generation
                </button>
              </div>
            )}

            {status === 'cancelled' && (
              <div className="bg-yellow-900 border border-yellow-700 rounded-lg p-4 mt-4">
                <p className="text-yellow-200">Generation was cancelled</p>
                <button
                  onClick={handleReset}
                  className="w-full mt-2 bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg transition"
                >
                  Start Over
                </button>
              </div>
            )}
          </div>
        )}

        <div className="mt-12 text-center text-gray-400 text-sm">
          <p>💡 Tip: Anime prompts work best. Try describing scenes, camera movements, and moods.</p>
        </div>
      </div>
    </main>
  );
}
