export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface SocialMedia {
  platform: string;
  url: string;
}

export interface ScanResult {
  company_name: string;
  website: string;
  summary: string;
  emails: string[];
  phone_numbers: string[];
  socials: SocialMedia[];
  addresses: string[];
  notes: string | null;
  sources: string[];
}

export interface Scan {
  id: number;
  website_url: string;
  company_name: string | null;
  summary: string | null;
  structured_data: ScanResult;
  created_at: string;
}

export interface ScanListItem {
  id: number;
  website_url: string;
  company_name: string | null;
  summary: string | null;
  created_at: string;
}

export interface ScanListResponse {
  total: number;
  scans: ScanListItem[];
  page: number;
  page_size: number;
  total_pages: number;
}