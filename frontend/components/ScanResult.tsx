'use client';

import { Mail, Phone, MapPin, Globe, FileText, ExternalLink, Download } from 'lucide-react';
import type { Scan } from '@/types';
import { format } from 'date-fns';

interface ScanResultProps {
  scan: Scan;
}

export default function ScanResult({ scan }: ScanResultProps) {
  const { structured_data, created_at } = scan;

  const handleExport = () => {
    const dataStr = JSON.stringify(structured_data, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${structured_data.company_name.replace(/\s+/g, '_')}_scan.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 space-y-6">
      {/* Header */}
      <div className="border-b pb-4 flex justify-between items-start">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">{structured_data.company_name}</h2>
          <a
            href={structured_data.website}
            target="_blank"
            rel="noopener noreferrer"
            className="text-indigo-600 hover:text-indigo-700 flex items-center gap-1 mt-1"
          >
            <Globe className="w-4 h-4" />
            {structured_data.website}
            <ExternalLink className="w-3 h-3" />
          </a>
          <p className="text-sm text-gray-500 mt-2">
            Scanned on {format(new Date(created_at), 'PPpp')}
          </p>
        </div>

        <button
          onClick={handleExport}
          className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center gap-2 text-sm font-medium"
        >
          <Download className="w-4 h-4" />
          Export JSON
        </button>
      </div>

      {/* Summary */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2 flex items-center gap-2">
          <FileText className="w-5 h-5 text-gray-600" />
          Summary
        </h3>
        <p className="text-gray-700 leading-relaxed">{structured_data.summary}</p>
      </div>

      {/* Emails */}
      {structured_data.emails.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <Mail className="w-5 h-5 text-gray-600" />
            Email Addresses ({structured_data.emails.length})
          </h3>
          <div className="flex flex-wrap gap-2">
            {structured_data.emails.map((email, idx) => (
              <a
                key={idx}
                href={`mailto:${email}`}
                className="px-3 py-1.5 bg-blue-50 text-blue-700 rounded-md hover:bg-blue-100 text-sm font-medium"
              >
                {email}
              </a>
            ))}
          </div>
        </div>
      )}

      {/* Phone Numbers */}
      {structured_data.phone_numbers.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <Phone className="w-5 h-5 text-gray-600" />
            Phone Numbers ({structured_data.phone_numbers.length})
          </h3>
          <div className="flex flex-wrap gap-2">
            {structured_data.phone_numbers.map((phone, idx) => (
              <a
                key={idx}
                href={`tel:${phone}`}
                className="px-3 py-1.5 bg-green-50 text-green-700 rounded-md hover:bg-green-100 text-sm font-medium"
              >
                {phone}
              </a>
            ))}
          </div>
        </div>
      )}

      {/* Social Media */}
      {structured_data.socials.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <Globe className="w-5 h-5 text-gray-600" />
            Social Media ({structured_data.socials.length})
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {structured_data.socials.map((social, idx) => (
              <a
                key={idx}
                href={social.url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center justify-between px-4 py-2 bg-purple-50 text-purple-700 rounded-md hover:bg-purple-100"
              >
                <span className="font-medium">{social.platform}</span>
                <ExternalLink className="w-4 h-4" />
              </a>
            ))}
          </div>
        </div>
      )}

      {/* Addresses */}
      {structured_data.addresses.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <MapPin className="w-5 h-5 text-gray-600" />
            Addresses ({structured_data.addresses.length})
          </h3>
          <div className="space-y-2">
            {structured_data.addresses.map((address, idx) => (
              <div key={idx} className="px-4 py-2 bg-gray-50 rounded-md text-gray-700">
                {address}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Notes */}
      {structured_data.notes && (
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Additional Notes</h3>
          <p className="text-gray-700 leading-relaxed bg-gray-50 p-4 rounded-md">
            {structured_data.notes}
          </p>
        </div>
      )}

      {/* Sources */}
      {structured_data.sources.length > 0 && (
        <div className="border-t pt-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-2">Sources</h3>
          <div className="space-y-1">
            {structured_data.sources.map((source, idx) => (
              <a
                key={idx}
                href={source}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-indigo-600 hover:text-indigo-700 flex items-center gap-1"
              >
                <ExternalLink className="w-3 h-3" />
                {source}
              </a>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
