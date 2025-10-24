import { ChartData } from './types';

interface CustomBarChartProps {
  chartData: ChartData;
  title: string;
  colors?: string[];
}

/**
 * Custom Bar Chart Component
 *
 * Renders a bar chart with automatic horizontal/vertical layout based on label length.
 * For long labels (>20 chars), displays horizontal bars.
 * For short labels, displays vertical bars.
 *
 * @example
 * ```tsx
 * <CustomBarChart
 *   chartData={{
 *     labels: ['Option A', 'Option B', 'Option C'],
 *     data: [10, 25, 15],
 *     backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56']
 *   }}
 *   title="Survey Responses"
 * />
 * ```
 */
export function CustomBarChart({ chartData, title, colors }: CustomBarChartProps) {
  const defaultColors = [
    '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
    '#FF9F40', '#FF6384', '#C9CBCF', '#4BC0C0', '#FF6384'
  ];

  const maxValue = Math.max(...chartData.data, 1); // Ensure at least 1 to avoid division by 0
  const hasLongLabels = chartData.labels.some(label => label.length > 20);

  // Direct pixel-based scaling for 500px container with better proportions
  const getScaledHeight = (value: number) => {
    if (value === 0) return '0px';
    if (value === maxValue) return '450px'; // Tallest bar uses most of 500px container
    const calculatedHeight = Math.max((value / maxValue) * 450, 200); // Min 200px for visibility while maintaining proportions
    return `${calculatedHeight}px`;
  };

  const containerHeight = hasLongLabels ? Math.max(chartData.labels.length * 80, 400) : 500;

  return (
    <div className="w-full">
      <h3 className="text-lg font-medium text-gray-900 mb-4 text-center">{title}</h3>
      <div
        className={`bg-white p-2 rounded-lg border ${hasLongLabels ? 'space-y-6' : 'flex items-end justify-center space-x-1'}`}
        style={{ height: `${containerHeight}px` }}
      >
        {chartData.labels.map((label, index) => {
          const value = chartData.data[index];
          const scaledHeight = getScaledHeight(value);
          const color = chartData.backgroundColor?.[index] || colors?.[index] || defaultColors[index % defaultColors.length];

          if (hasLongLabels) {
            // Horizontal bar layout for long labels
            return (
              <div key={index} className="flex items-center space-x-3">
                <div className="w-32 text-sm text-gray-700 text-right truncate" title={label}>
                  {label}
                </div>
                <div className="flex-1 bg-gray-200 rounded-lg h-12 relative">
                  <div
                    className="h-12 rounded-lg flex items-center justify-end pr-4 text-white text-sm font-semibold transition-all duration-500"
                    style={{
                      backgroundColor: color,
                      width: `${Math.max((value / maxValue) * 100, 60)}%`
                    }}
                  >
                    {value > 0 && (
                      <span className="text-white drop-shadow">{value}</span>
                    )}
                  </div>
                </div>
              </div>
            );
          } else {
            // Vertical bar layout for short labels
            return (
              <div key={index} className="flex flex-col items-center space-y-2 flex-1 min-w-0">
                <div
                  className="w-full rounded-t-lg transition-all duration-500 flex items-end justify-center text-white text-xs font-semibold pb-1"
                  style={{
                    backgroundColor: color,
                    height: scaledHeight,
                    minHeight: value > 0 ? '200px' : '20px'
                  }}
                >
                  {value > 0 && <span className="drop-shadow">{value}</span>}
                </div>
                <div className="text-xs text-gray-700 text-center truncate w-full" title={label}>
                  {label}
                </div>
              </div>
            );
          }
        })}
      </div>
      <div className="mt-2 text-xs text-gray-500 text-center">
        Total responses: {chartData.data.reduce((a, b) => a + b, 0)}
      </div>
    </div>
  );
}

export default CustomBarChart;
