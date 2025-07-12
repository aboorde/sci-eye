/**
 * Chart.js configuration helpers
 */

export const chartColors = {
  primary: 'rgb(14, 165, 233)',
  secondary: 'rgb(139, 92, 246)',
  accent: 'rgb(16, 185, 129)',
  success: 'rgb(54, 211, 153)',
  warning: 'rgb(251, 189, 35)',
  error: 'rgb(248, 114, 114)',
  info: 'rgb(58, 191, 248)'
};

export const chartColorsWithAlpha = (alpha = 0.2) => ({
  primary: `rgba(14, 165, 233, ${alpha})`,
  secondary: `rgba(139, 92, 246, ${alpha})`,
  accent: `rgba(16, 185, 129, ${alpha})`,
  success: `rgba(54, 211, 153, ${alpha})`,
  warning: `rgba(251, 189, 35, ${alpha})`,
  error: `rgba(248, 114, 114, ${alpha})`,
  info: `rgba(58, 191, 248, ${alpha})`
});

/**
 * Generate chart colors for a dataset
 * @param {number} count - Number of colors needed
 * @returns {Array} Array of colors
 */
export function generateChartColors(count) {
  const baseColors = Object.values(chartColors);
  const colors = [];
  
  for (let i = 0; i < count; i++) {
    colors.push(baseColors[i % baseColors.length]);
  }
  
  return colors;
}

/**
 * Base chart options
 */
export const baseChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom',
      labels: {
        padding: 16,
        usePointStyle: true,
        font: {
          family: 'Inter',
          size: 12
        }
      }
    },
    tooltip: {
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      padding: 12,
      cornerRadius: 8,
      titleFont: {
        family: 'Inter',
        size: 14,
        weight: '600'
      },
      bodyFont: {
        family: 'Inter',
        size: 13
      }
    }
  }
};

/**
 * Create pie chart config
 * @param {Array} labels - Chart labels
 * @param {Array} data - Chart data
 * @param {Object} options - Additional options
 * @returns {Object} Chart configuration
 */
export function createPieChartConfig(labels, data, options = {}) {
  return {
    type: 'pie',
    data: {
      labels,
      datasets: [{
        data,
        backgroundColor: generateChartColors(data.length),
        borderWidth: 2,
        borderColor: '#fff'
      }]
    },
    options: {
      ...baseChartOptions,
      ...options,
      plugins: {
        ...baseChartOptions.plugins,
        ...options.plugins,
        datalabels: {
          color: '#fff',
          font: {
            weight: 'bold',
            size: 12
          },
          formatter: (value, ctx) => {
            const sum = ctx.dataset.data.reduce((a, b) => a + b, 0);
            const percentage = ((value / sum) * 100).toFixed(1) + '%';
            return percentage;
          }
        }
      }
    }
  };
}

/**
 * Create line chart config
 * @param {Array} labels - Chart labels
 * @param {Array} datasets - Chart datasets
 * @param {Object} options - Additional options
 * @returns {Object} Chart configuration
 */
export function createLineChartConfig(labels, datasets, options = {}) {
  return {
    type: 'line',
    data: {
      labels,
      datasets: datasets.map((dataset, index) => ({
        ...dataset,
        borderColor: Object.values(chartColors)[index % Object.values(chartColors).length],
        backgroundColor: Object.values(chartColorsWithAlpha(0.1))[index % Object.values(chartColors).length],
        borderWidth: 2,
        tension: 0.4,
        pointRadius: 4,
        pointHoverRadius: 6
      }))
    },
    options: {
      ...baseChartOptions,
      ...options,
      scales: {
        x: {
          grid: {
            display: false
          },
          ticks: {
            font: {
              family: 'Inter',
              size: 11
            }
          }
        },
        y: {
          beginAtZero: true,
          grid: {
            color: 'rgba(0, 0, 0, 0.05)'
          },
          ticks: {
            font: {
              family: 'Inter',
              size: 11
            }
          }
        }
      }
    }
  };
}

/**
 * Create bar chart config
 * @param {Array} labels - Chart labels
 * @param {Array} datasets - Chart datasets
 * @param {Object} options - Additional options
 * @returns {Object} Chart configuration
 */
export function createBarChartConfig(labels, datasets, options = {}) {
  return {
    type: 'bar',
    data: {
      labels,
      datasets: datasets.map((dataset, index) => ({
        ...dataset,
        backgroundColor: Object.values(chartColorsWithAlpha(0.8))[index % Object.values(chartColors).length],
        borderColor: Object.values(chartColors)[index % Object.values(chartColors).length],
        borderWidth: 2,
        borderRadius: 8,
        borderSkipped: false
      }))
    },
    options: {
      ...baseChartOptions,
      ...options,
      scales: {
        x: {
          grid: {
            display: false
          },
          ticks: {
            font: {
              family: 'Inter',
              size: 11
            }
          }
        },
        y: {
          beginAtZero: true,
          grid: {
            color: 'rgba(0, 0, 0, 0.05)'
          },
          ticks: {
            font: {
              family: 'Inter',
              size: 11
            }
          }
        }
      }
    }
  };
}