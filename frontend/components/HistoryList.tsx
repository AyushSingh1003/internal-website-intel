'use client';

import Link from 'next/link';
import { format, parseISO } from 'date-fns';
import { ExternalLink, Eye, Trash2 } from 'lucide-react';
import type { ScanListItem } from '@/types';

interface HistoryListProps {
  scans: ScanListItem[];
  onDelete: (id: number) => void;
}

export default function HistoryList({ scans, onDelete }: HistoryListProps) {
  if (scans.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-12 text-center">
        <p className="text-gray-500 text-lg">No scans yet</p>
        <p className="text-gray-400 text-sm mt-2">Start by analyzing a website from the dashboard</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Company
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Website
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Scanned
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {scans.map((scan) => (
              <tr key={scan.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">
                    {scan.company_name || 'Unknown Company'}
                  </div>
                  <div className="text-sm text-gray-500 truncate max-w-md">
                    {scan.summary}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <a
                    href={scan.website_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-indigo-600 hover:text-indigo-700 flex items-center gap-1"
                  >
                    {new URL(scan.website_url).hostname}
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {format(parseISO(/[Zz]|[+-]\\d{2}:?\\d{2}$/.test(scan.created_at) ? scan.created_at : `${scan.created_at}Z`), 'PPp')}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <div className="flex justify-end gap-2">
                    <Link
                      href={`/history/${scan.id}`}
                      className="text-indigo-600 hover:text-indigo-900 p-2 hover:bg-indigo-50 rounded"
                    >
                      <Eye className="w-5 h-5" />
                    </Link>
                    <button
                      onClick={() => onDelete(scan.id)}
                      className="text-red-600 hover:text-red-900 p-2 hover:bg-red-50 rounded"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
