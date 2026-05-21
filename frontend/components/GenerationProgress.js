'use client';

export default function GenerationProgress({ status, progress, message }) {
  if (!status || status === 'idle') {
    return null;
  }

  return (
    <div className="w-full bg-gray-800 border border-gray-700 rounded-lg p-6">
      <h3 className="text-lg font-semibold text-white mb-4">Generation in Progress</h3>

      <div className="space-y-3">
        <div>
          <div className="flex justify-between text-sm mb-2">
            <span className="text-gray-300">Progress</span>
            <span className="text-gray-400">{progress || 0}%</span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2 overflow-hidden">
            <div
              className="bg-blue-500 h-full transition-all duration-300"
              style={{ width: `${progress || 0}%` }}
            />
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <div className="animate-spin">
            <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full" />
          </div>
          <p className="text-gray-300 text-sm">{message || 'Processing...'}</p>
        </div>
      </div>
    </div>
  );
}
