"use client";
import { useState } from 'react';
import { uploadFile, analyzeData } from '@/lib/apiService';

export default function Home() {
  const [file, setFile] = useState(null);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async () => {
    if (!file) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const uploadResult = await uploadFile(file);
      const analysis = await analyzeData(uploadResult.file_path);
      setResults(analysis);
    } catch (err) {
      setError('Failed to process file');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">SaaS User Growth Analyzer</h1>
      
      <div className="mb-4">
        <input 
          type="file" 
          accept=".csv" 
          onChange={handleFileChange} 
          disabled={loading}
          className="mb-2"
        />
        <button 
          onClick={handleSubmit} 
          disabled={loading}
          className="bg-blue-500 text-white px-4 py-2 rounded disabled:bg-gray-400"
        >
          {loading ? 'Processing...' : 'Analyze'}
        </button>
      </div>

      {error && <div className="text-red-500 mb-4">{error}</div>}

      {results && (
        <div>
          <h2 className="text-xl font-semibold mb-2">Analysis Results</h2>
          <pre>{JSON.stringify(results, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
