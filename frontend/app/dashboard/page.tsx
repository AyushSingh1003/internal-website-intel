'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { isAuthenticated } from '@/lib/auth';
import { createScan } from '@/lib/api';
import ScanForm from '@/components/ScanForm';
import ScanResult from '@/components/ScanResult';
import type { Scan } from '@/types';
import { AlertCircle, CheckCircle2, Loader2 } from 'lucide-react';

export default function DashboardPage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [scan, setScan] = useState<Scan | null>(null);
  const [progress, setProgress] = useState(0);
  const [progressMessage, setProgressMessage] = useState('');
  const router = useRouter();

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login');
    }
  }, [router]);

  const simulateProgress = () => {
    let currentProgress = 0;
    const messages = [
      'Initializing scraper...',
      'Fetching website content...',
      'Discovering contact pages...',
      'Extracting contact information...',
      'Processing with AI...',
      'Validating results...',
      'Saving to database...'
    ];

    const interval = setInterval(() => {
      currentProgress += Math.random() * 15;
      if (currentProgress > 90) currentProgress = 90;

      setProgress(Math.floor(currentProgress));

      const messageIndex = Math.floor(currentProgress / 15);
      if (messageIndex < messages.length) {
        setProgressMessage(messages[messageIndex]);
      }
    }, 2000);

    return () => clearInterval(interval);
  };

  const handleScan = async (url: string) => {
    setLoading(true);
    setError('');
    setScan(null);
    setProgress(0);

    const cleanup = simulateProgress();

    try {
      const result = await createScan(url);
      setProgress(100);
      setProgressMessage('Complete!');
      setTimeout(() => {
        setScan(result);
        cleanup();
      }, 500);
    } catch (err: any) {
      cleanup();
      if (err.response?.status === 429) {
        setError('Rate limit exceeded. Please wait a few minutes before trying again.');
      } else {
        setError(err.response?.data?.detail || 'Failed to scan website. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  if (!isAuthenticated()) {
    return null;
  }

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Website Intelligence Scanner</h1>
        <p className="text-gray-600">
          Analyze any company website to extract contact information, social media profiles, and more.
        </p>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <ScanForm onSubmit={handleScan} loading={loading} />
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-8 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" />
          <div>
            <h3 className="font-semibold text-red-900">Error</h3>
            <p className="text-red-700 text-sm mt-1">{error}</p>
          </div>
        </div>
      )}

      {loading && (
        <div className="bg-white rounded-lg shadow-md p-8">
          <div className="text-center mb-6">
            <Loader2 className="w-12 h-12 animate-spin text-indigo-600 mx-auto mb-4" />
            <p className="text-gray-600 font-medium text-lg">Analyzing website...</p>
            <p className="text-sm text-gray-500 mt-2">{progressMessage}</p>
          </div>

          <div className="w-full bg-gray-200 rounded-full h-3 mb-2">
            <div
              className="bg-indigo-600 h-3 rounded-full transition-all duration-500 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="text-center text-sm text-gray-600">{progress}%</p>

          <div className="mt-6 grid grid-cols-3 gap-4 text-center">
            <div className="p-3 bg-gray-50 rounded-lg">
              <div className="text-2xl mb-1">🔍</div>
              <div className="text-xs text-gray-600">Scraping</div>
            </div>
            <div className="p-3 bg-gray-50 rounded-lg">
              <div className="text-2xl mb-1">🤖</div>
              <div className="text-xs text-gray-600">AI Processing</div>
            </div>
            <div className="p-3 bg-gray-50 rounded-lg">
              <div className="text-2xl mb-1">💾</div>
              <div className="text-xs text-gray-600">Saving</div>
            </div>
          </div>
        </div>
      )}

      {scan && !loading && (
        <div className="space-y-4">
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-center gap-3">
            <CheckCircle2 className="w-5 h-5 text-green-600 flex-shrink-0" />
            <p className="text-green-800 font-medium">Scan completed successfully!</p>
          </div>
          <ScanResult scan={scan} />
        </div>
      )}
    </div>
  );
}