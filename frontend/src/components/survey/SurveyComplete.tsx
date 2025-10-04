"use client";

import { useRouter } from "next/navigation";
import { CheckCircleIcon } from "@heroicons/react/24/solid";

interface SurveyCompleteProps {
  surveyName: string;
}

export default function SurveyComplete({ surveyName }: SurveyCompleteProps) {
  const router = useRouter();

  return (
    <div className="bg-white rounded-lg shadow-lg p-8 text-center">
      <div className="mb-6">
        <CheckCircleIcon className="w-20 h-20 text-green-500 mx-auto mb-4" />
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Survey Completed!</h2>
        <p className="text-lg text-gray-600 mb-4">
          Thank you for completing <span className="font-semibold">&ldquo;{surveyName}&rdquo;</span>
        </p>
      </div>

      <div className="bg-green-50 border border-green-200 rounded-lg p-6 mb-6">
        <h3 className="text-lg font-semibold text-green-800 mb-2">What happens next?</h3>
        <ul className="text-sm text-green-700 text-left space-y-2">
          <li>• Your responses have been successfully submitted</li>
          <li>• Our team will review your submission</li>
          <li>• You may be contacted if additional information is needed</li>
          <li>• Thank you for your valuable participation!</li>
        </ul>
      </div>

      <div className="space-y-4">
        <button
          onClick={() => router.push('/')}
          className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 transition-colors"
        >
          Return to Home
        </button>

        <p className="text-xs text-gray-500">
          Survey ID: {Date.now().toString(36)} • Completed at {new Date().toLocaleString()}
        </p>
      </div>
    </div>
  );
}