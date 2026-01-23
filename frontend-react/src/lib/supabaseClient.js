
import { createClient } from '@supabase/supabase-js';

// TODO: Replace with env vars or user input
const supabaseUrl = 'https://weofgczcilzzwqzqjtme.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Indlb2ZnY3pjaWx6endxenFqdG1lIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjkwNzM1MzQsImV4cCI6MjA4NDY0OTUzNH0.TiYYvxTM0M0O0brcuJYG-n9uEZQpxyZh8TNHMpjdmh0';

export const supabase = createClient(supabaseUrl, supabaseKey);
