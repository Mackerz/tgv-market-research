'use client'

import Link from 'next/link'
import { XCircleIcon } from '@heroicons/react/24/outline'

export default function SurveyUnavailablePage() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        <div className="bg-white rounded-lg shadow-lg p-8 text-center">
          {/* Icon */}
          <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-red-100 mb-6">
            <XCircleIcon className="h-10 w-10 text-red-600" />
          </div>

          {/* Title */}
          <h1 className="text-2xl font-bold text-gray-900 mb-3">
            Survey Not Available
          </h1>

          {/* Message */}
          <p className="text-gray-600 mb-6">
            We're sorry, but this survey is currently unavailable. It may have been closed or is temporarily disabled.
          </p>

          {/* Additional Info */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <p className="text-sm text-blue-800">
              Please contact the survey administrator if you believe this is an error, or check back later.
            </p>
          </div>

          {/* Action Button */}
          <Link
            href="/"
            className="inline-block w-full px-6 py-3 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
          >
            Return to Home
          </Link>
        </div>
      </div>
    </div>
  )
}
