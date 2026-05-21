'use client';

export default function VideoPreview({ jobId, onReset }) {
  const videoUrl = `/api/outputs/${jobId}`;

  return (
    <div className="w-full bg-gray-800 border border-gray-700 rounded-lg p-6">
      <h3 className="text-lg font-semibold text-white mb-4">Generated Video</h3>

      <div className="bg-black rounded-lg overflow-hidden mb-4">
        <video
          src={videoUrl}
          controls
          className="w-full h-96 object-contain"
        />
      </div>

      <div className="flex gap-3">
        <a
          href={videoUrl}
          download={`video-${jobId}.mp4`}
          className="flex-1 bg-green-600 hover:bg-green-700 text-white font-semibold py-2 px-4 rounded-lg text-center transition"
        >
          Download Video
        </a>
        <button
          onClick={onReset}
          className="flex-1 bg-gray-700 hover:bg-gray-600 text-white font-semibold py-2 px-4 rounded-lg transition"
        >
          Generate Another
        </button>
      </div>
    </div>
  );
}
