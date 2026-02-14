// sync-athena: Supabase Edge Function for automated Athena memory sync
// Triggers: GitHub webhook or cron schedule
// Purpose: Fetch latest .md files from GitHub repo and sync to Supabase

import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get("SERVICE_ROLE_KEY")!;
const GITHUB_TOKEN = Deno.env.get("GITHUB_TOKEN")!;
const GOOGLE_API_KEY = Deno.env.get("GOOGLE_API_KEY")!;

const GITHUB_OWNER = "winstonkoh87";
const GITHUB_REPO = "Athena";
const GITHUB_BRANCH = "main";

interface GitHubFile {
  name: string;
  path: string;
  type: string;
  download_url: string | null;
}

interface EmbeddingResponse {
  embedding: { values: number[] };
}

// Generate embedding using Google Gemini
async function getEmbedding(text: string): Promise<number[]> {
  const truncatedText = text.slice(0, 32000); // Truncate to ~8000 tokens
  
  const response = await fetch(
    `https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key=${GOOGLE_API_KEY}`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        model: "models/text-embedding-004",
        content: { parts: [{ text: truncatedText }] },
      }),
    }
  );

  if (!response.ok) {
    throw new Error(`Embedding API error: ${response.statusText}`);
  }

  const data: EmbeddingResponse = await response.json();
  return data.embedding.values;
}

// Fetch files from GitHub directory
async function fetchGitHubDirectory(path: string): Promise<GitHubFile[]> {
  const url = `https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/contents/${path}?ref=${GITHUB_BRANCH}`;
  
  const response = await fetch(url, {
    headers: {
      Authorization: `Bearer ${GITHUB_TOKEN}`,
      Accept: "application/vnd.github.v3+json",
    },
  });

  if (!response.ok) {
    throw new Error(`GitHub API error: ${response.statusText}`);
  }

  return await response.json();
}

// Fetch file content from GitHub
async function fetchFileContent(url: string): Promise<string> {
  const response = await fetch(url, {
    headers: {
      Authorization: `Bearer ${GITHUB_TOKEN}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch file: ${response.statusText}`);
  }

  return await response.text();
}

// Parse session filename
function parseSessionFilename(filename: string): { date: string; sessionNum: number } | null {
  const match = filename.match(/(\d{4}-\d{2}-\d{2})-session-(\d+)\.md/);
  if (match) {
    return { date: match[1], sessionNum: parseInt(match[2]) };
  }
  return null;
}

// Extract title from markdown
function extractTitle(content: string): string {
  const lines = content.split("\n");
  for (const line of lines) {
    if (line.startsWith("# ")) {
      return line.slice(2).trim();
    }
  }
  return "Untitled";
}

// Extract tags from content
function extractTags(content: string): string[] {
  const tags = content.match(/`#([a-zA-Z0-9-]+)`/g) || [];
  return [...new Set(tags.map((t) => t.slice(2, -1)))].slice(0, 10);
}

// Sync sessions
async function syncSessions(supabase: ReturnType<typeof createClient>): Promise<{ synced: number; skipped: number; errors: number }> {
  let synced = 0;
  let skipped = 0;
  let errors = 0;

  try {
    const files = await fetchGitHubDirectory(".context/memories/session_logs");
    
    for (const file of files) {
      if (file.type !== "file" || !file.name.endsWith(".md") || !file.download_url) {
        continue;
      }

      const parsed = parseSessionFilename(file.name);
      if (!parsed) {
        console.log(`Skipping invalid format: ${file.name}`);
        skipped++;
        continue;
      }

      // Check if already exists
      const { data: existing } = await supabase
        .from("sessions")
        .select("id")
        .eq("file_path", file.path)
        .single();

      if (existing) {
        console.log(`Already exists: ${file.name}`);
        skipped++;
        continue;
      }

      // Fetch content and generate embedding
      const content = await fetchFileContent(file.download_url);
      const title = extractTitle(content);
      const embedding = await getEmbedding(content);

      // Insert
      const { error } = await supabase.from("sessions").insert({
        date: parsed.date,
        session_number: parsed.sessionNum,
        title,
        content,
        embedding,
        file_path: file.path,
      });

      if (error) {
        console.error(`Error syncing ${file.name}:`, error);
        errors++;
      } else {
        console.log(`Synced: ${file.name}`);
        synced++;
      }
    }
  } catch (error) {
    console.error("Error syncing sessions:", error);
    errors++;
  }

  return { synced, skipped, errors };
}

// Sync case studies
async function syncCaseStudies(supabase: ReturnType<typeof createClient>): Promise<{ synced: number; skipped: number; errors: number }> {
  let synced = 0;
  let skipped = 0;
  let errors = 0;

  try {
    const files = await fetchGitHubDirectory(".context/memories/case_studies");
    
    for (const file of files) {
      if (file.type !== "file" || !file.name.endsWith(".md") || !file.download_url) {
        continue;
      }

      // Check if already exists
      const { data: existing } = await supabase
        .from("case_studies")
        .select("id")
        .eq("file_path", file.path)
        .single();

      if (existing) {
        console.log(`Already exists: ${file.name}`);
        skipped++;
        continue;
      }

      // Fetch content and generate embedding
      const content = await fetchFileContent(file.download_url);
      const title = extractTitle(content);
      const tags = extractTags(content);
      const code = file.name.match(/^(CS-\d+)/)?.[1] || file.name.replace(".md", "");
      const embedding = await getEmbedding(content);

      // Insert
      const { error } = await supabase.from("case_studies").insert({
        code,
        title,
        content,
        tags,
        embedding,
        file_path: file.path,
      });

      if (error) {
        console.error(`Error syncing ${file.name}:`, error);
        errors++;
      } else {
        console.log(`Synced: ${file.name}`);
        synced++;
      }
    }
  } catch (error) {
    console.error("Error syncing case studies:", error);
    errors++;
  }

  return { synced, skipped, errors };
}

serve(async (req: Request) => {
  try {
    // Verify request (optional: check for GitHub webhook signature or cron secret)
    const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);

    console.log("Starting Athena sync...");

    const sessionResult = await syncSessions(supabase);
    const caseStudyResult = await syncCaseStudies(supabase);

    const result = {
      success: true,
      timestamp: new Date().toISOString(),
      sessions: sessionResult,
      caseStudies: caseStudyResult,
    };

    console.log("Sync complete:", result);

    return new Response(JSON.stringify(result), {
      headers: { "Content-Type": "application/json" },
      status: 200,
    });
  } catch (error) {
    console.error("Sync error:", error);
    return new Response(
      JSON.stringify({ success: false, error: "Internal Server Error" }),
      {
        headers: { "Content-Type": "application/json" },
        status: 500,
      }
    );
  }
});
