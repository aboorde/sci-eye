import { base } from '$app/paths';

/**
 * Loads all pharma news JSON files from the data directory
 * @returns {Promise<Array>} Array of monitoring run data
 */
export async function loadAllData() {
  try {
    // In production, we'll need to know which files exist
    // For now, we'll try to load files based on a pattern
    const dataFiles = await getDataFileList();
    const allData = [];

    for (const file of dataFiles) {
      try {
        const response = await fetch(`${base}/data/${file}`);
        if (response.ok) {
          const data = await response.json();
          allData.push({
            filename: file,
            ...data
          });
        }
      } catch (error) {
        console.error(`Error loading ${file}:`, error);
      }
    }

    return allData.sort((a, b) => 
      new Date(b.run_timestamp) - new Date(a.run_timestamp)
    );
  } catch (error) {
    console.error('Error loading data:', error);
    return [];
  }
}

/**
 * Get list of data files from manifest
 * The manifest is generated at build time and includes all JSON files in /data
 */
async function getDataFileList() {
  try {
    const response = await fetch(`${base}/data/manifest.json`);
    if (response.ok) {
      const manifest = await response.json();
      return manifest.files;
    }
  } catch (error) {
    console.log('No manifest found, returning empty array');
  }

  // Return empty array if no manifest - all JSON files will be included at build time
  return ['pharma_news_20250714_012155.json'];
}

/**
 * Aggregates all articles from multiple monitoring runs
 * @param {Array} allData - Array of monitoring run data
 * @returns {Array} Flat array of all articles with run metadata
 */
export function aggregateArticles(allData) {
  const articles = [];
  
  for (const run of allData) {
    for (const article of run.articles || []) {
      articles.push({
        ...article,
        run_timestamp: run.run_timestamp,
        run_id: run.filename
      });
    }
  }

  return articles;
}

/**
 * Get unique topics from all articles
 * @param {Array} articles - Array of articles
 * @returns {Array} Array of unique topic names
 */
export function getUniqueTopics(articles) {
  const topicsSet = new Set();
  
  for (const article of articles) {
    for (const topic of article.topics || []) {
      topicsSet.add(topic);
    }
  }

  return Array.from(topicsSet).sort();
}

/**
 * Get unique sources from all articles
 * @param {Array} articles - Array of articles
 * @returns {Array} Array of unique source names
 */
export function getUniqueSources(articles) {
  const sourcesSet = new Set();
  
  for (const article of articles) {
    if (article.source_feed) {
      sourcesSet.add(article.source_feed);
    }
  }

  return Array.from(sourcesSet).sort();
}