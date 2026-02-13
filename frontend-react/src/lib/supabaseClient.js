
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://weofgczcilzzwqzqjtme.supabase.co';
const supabaseKey = import.meta.env.VITE_SUPABASE_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Indlb2ZnY3pjaWx6endxenFqdG1lIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjkwNzM1MzQsImV4cCI6MjA4NDY0OTUzNH0.TiYYvxTM0M0O0brcuJYG-n9uEZQpxyZh8TNHMpjdmh0';

export const supabase = createClient(supabaseUrl, supabaseKey);
