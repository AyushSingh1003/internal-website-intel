'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { isAuthenticated } from '@/lib/auth';
import { getScans, deleteScan } from '@/lib/api';
import HistoryList from '@/components/HistoryList';
import type { ScanListResponse } from '@/types';
import { ChevronLeft, ChevronRight, Loader2 } from 'lucide-react';

export default function HistoryPage() {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<ScanListResponse | null>(null);
  const [page, setPage] = useState(1);
  const [deleting, setDeleting] = useState<number | null>(null);
  const router = useRouter();

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login');
      return;
    }
    fetchScans();
  }, [page, router]);

  const fetchScans = async () => {
    setLoading(true);
    try {
      const result = await getScans(page, 10);
      setData(result);
    } catch (err) {
      console.error('Failed to fetch scans:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this scan?')) {
      return;
    }

    setDeleting(id);
    try {
      await deleteScan(id);
      await fetchScans(); // Refresh list
    } catch (err) {
      console.error('Failed to delete scan:', err);
      alert('Failed to delete scan');
    } finally {
      setDeleting(null);
    }
  };

  if (!isAuthenticated()) {
    return null;
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Scan History</h1>
        <p className="text-gray-600">
          View and manage all previously scanned websites
        </p>
      </div>

      {loading ? (
        <div className="bg-white rounded-lg shadow-md p-12 text-center">
          <Loader2 className="w-12 h-12 animate-spin text-indigo-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading history...</p>
        </div>
      ) : data ? (
        <>
          <HistoryList scans={data.scans} onDelete={handleDelete} />

          {/* Pagination */}
          {data.total_pages > 1 && (
            <div className="mt-6 flex items-center justify-between bg-white px-4 py-3 rounded-lg shadow-md">
              <div className="text-sm text-gray-700">
                Page <span className="font-medium">{data.page}</span> of{' '}
                <span className="font-medium">{data.total_pages}</span>
                {' · '}
                <span className="font-medium">{data.total}</span> total scans
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => setPage(page - 1)}
                  disabled={page === 1}
                  className="px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1"
                >
                  <ChevronLeft className="w-4 h-4" />
                  Previous
                </button>
                <button
                  onClick={() => setPage(page + 1)}
                  disabled={page === data.total_pages}
                  className="px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1"
                >
                  Next
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}
        </>
      ) : (
        <div className="bg-white rounded-lg shadow-md p-12 text-center">
          <p className="text-gray-500">Failed to load scan history</p>
        </div>
      )}
    </div>
  );
}