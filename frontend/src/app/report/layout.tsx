import ProtectedRoute from '@/components/ProtectedRoute'

export default function ReportLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return <ProtectedRoute>{children}</ProtectedRoute>
}
