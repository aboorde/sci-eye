import { format, formatDistanceToNow, parseISO } from 'date-fns';

/**
 * Format a date string
 * @param {string} dateString - ISO date string
 * @param {string} formatString - date-fns format string
 * @returns {string} Formatted date
 */
export function formatDate(dateString, formatString = 'MMM d, yyyy') {
  if (!dateString) return 'Unknown';
  try {
    return format(parseISO(dateString), formatString);
  } catch {
    return dateString;
  }
}

/**
 * Format a date as relative time
 * @param {string} dateString - ISO date string
 * @returns {string} Relative time string
 */
export function formatRelativeTime(dateString) {
  if (!dateString) return 'Unknown';
  try {
    return formatDistanceToNow(parseISO(dateString), { addSuffix: true });
  } catch {
    return dateString;
  }
}

/**
 * Format a number as percentage
 * @param {number} value - Value to format
 * @param {number} decimals - Number of decimal places
 * @returns {string} Formatted percentage
 */
export function formatPercentage(value, decimals = 1) {
  return `${value.toFixed(decimals)}%`;
}

/**
 * Format a confidence score
 * @param {number} score - Confidence score (0-1)
 * @returns {string} Formatted score
 */
export function formatConfidence(score) {
  return `${(score * 100).toFixed(0)}%`;
}

/**
 * Truncate text to a maximum length
 * @param {string} text - Text to truncate
 * @param {number} maxLength - Maximum length
 * @returns {string} Truncated text
 */
export function truncateText(text, maxLength = 150) {
  if (!text || text.length <= maxLength) return text;
  return text.substring(0, maxLength).trim() + '...';
}

/**
 * Format article count
 * @param {number} count - Article count
 * @returns {string} Formatted count
 */
export function formatArticleCount(count) {
  if (count === 0) return 'No articles';
  if (count === 1) return '1 article';
  return `${count} articles`;
}

/**
 * Get color for confidence score
 * @param {number} score - Confidence score (0-1)
 * @returns {string} Tailwind color class
 */
export function getConfidenceColor(score) {
  if (score >= 0.9) return 'text-success';
  if (score >= 0.7) return 'text-primary';
  if (score >= 0.5) return 'text-warning';
  return 'text-error';
}

/**
 * Get badge color for topic
 * @param {string} topic - Topic name
 * @returns {string} Tailwind color classes
 */
export function getTopicColor(topic) {
  // Hash the topic name to get a consistent color
  const colors = [
    'bg-primary/10 text-primary',
    'bg-secondary/10 text-secondary',
    'bg-accent/10 text-accent',
    'bg-info/10 text-info',
    'bg-success/10 text-success',
    'bg-warning/10 text-warning'
  ];
  
  let hash = 0;
  for (let i = 0; i < topic.length; i++) {
    hash = topic.charCodeAt(i) + ((hash << 5) - hash);
  }
  
  return colors[Math.abs(hash) % colors.length];
}

/**
 * Format file size
 * @param {number} bytes - File size in bytes
 * @returns {string} Formatted size
 */
export function formatFileSize(bytes) {
  const units = ['B', 'KB', 'MB', 'GB'];
  let size = bytes;
  let unitIndex = 0;
  
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex++;
  }
  
  return `${size.toFixed(1)} ${units[unitIndex]}`;
}

/**
 * Get icon for source
 * @param {string} source - Source name
 * @returns {string} Lucide icon name
 */
export function getSourceIcon(source) {
  const iconMap = {
    'FierceBiotech': 'Microscope',
    'FiercePharma': 'Pill',
    'Evaluate Vantage': 'TrendingUp',
    'BioPharma Dive': 'Waves',
    'Pharmaceutical Technology': 'Cpu'
  };
  
  return iconMap[source] || 'FileText';
}