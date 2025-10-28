/**
 * SubmissionsStats Component
 * Displays summary statistics for submissions
 */

interface SubmissionsStatsProps {
  totalCount: number;
  approvedCount: number;
  rejectedCount: number;
  pendingCount: number;
}

export default function SubmissionsStats({
  totalCount,
  approvedCount,
  rejectedCount,
  pendingCount,
}: SubmissionsStatsProps) {
  const stats = [
    {
      label: 'Total',
      value: totalCount,
      color: 'bg-[#F5E8F0] text-[#4E0036]',
      icon: '📊',
    },
    {
      label: 'Approved',
      value: approvedCount,
      color: 'bg-green-100 text-green-800',
      icon: '✅',
    },
    {
      label: 'Rejected',
      value: rejectedCount,
      color: 'bg-red-100 text-red-800',
      icon: '❌',
    },
    {
      label: 'Pending',
      value: pendingCount,
      color: 'bg-yellow-100 text-yellow-800',
      icon: '⏳',
    },
  ];

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {stats.map((stat) => (
        <div
          key={stat.label}
          className={`${stat.color} rounded-lg p-4 shadow-sm`}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium opacity-80">{stat.label}</p>
              <p className="text-2xl font-bold mt-1">{stat.value}</p>
            </div>
            <div className="text-3xl opacity-50">{stat.icon}</div>
          </div>
        </div>
      ))}
    </div>
  );
}
