'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { isAuthenticated } from '@/lib/auth';
import { getScanById } from '@/lib/api';
import ScanResult from '@/components/ScanResult';
import type { Scan } from '@/types';
import { ArrowLeft, Loader2 } from 'lucide-react';
import Link from 'next/link';

export default function ScanDetailPage() {
  const [loading, setLoading] = useState(true);
  const [scan, setScan] = useState<Scan | null>(null);
  const [error, setError] = useState('');
  const router = useRouter();
  const params = useParams();
  const id = params.id as string;

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/login');
      return;
    }

    const fetchScan = async () => {
      setLoading(true);
      setError('');
      try {
        const result = await getScanById(parseInt(id));
        setScan(result);
      } catch (err: any) {
        setError(err.response?.status === 404 ? 'Scan not found' : 'Failed to load scan');
      } finally {
        setLoading(false);
      }
    };

    fetchScan();
  }, [id, router]);

  if (!isAuthenticated()) {
    return null;
  }

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <Link
        href="/history"
        className="inline-flex items-center gap-2 text-indigo-600 hover:text-indigo-700 mb-6"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to History
      </Link>

      {loading ? (
        <div className="bg-white rounded-lg shadow-md p-12 text-center">
          <Loader2 className="w-12 h-12 animate-spin text-indigo-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading scan details...</p>
        </div>
      ) : error ? (
        <div className="bg-white rounded-lg shadow-md p-12 text-center">
          <p className="text-red-600 text-lg">{error}</p>
        </div>
      ) : scan ? (
        <ScanResult scan={scan} />
      ) : null}
    </div>
  );
}