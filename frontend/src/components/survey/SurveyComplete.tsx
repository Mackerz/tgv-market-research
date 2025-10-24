"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { CheckCircleIcon } from "@heroicons/react/24/solid";

interface SurveyCompleteProps {
  surveyName: string;
  completeRedirectUrl?: string;
  externalUserId?: string | null;
  isScreenedOut?: boolean;
}

export default function SurveyComplete({ surveyName, completeRedirectUrl, externalUserId, isScreenedOut = false }: SurveyCompleteProps) {
  const router = useRouter();
  const [redirecting, setRedirecting] = useState(false);
  const [countdown, setCountdown] = useState(5);

  useEffect(() => {
    // If there's a redirect URL, redirect after showing success message briefly
    if (completeRedirectUrl) {
      setRedirecting(true);

      // Build redirect URL with external_user_id if provided
      let redirectUrl = completeRedirectUrl;
      if (externalUserId) {
        const separator = redirectUrl.includes('?') ? '&' : '?';
        redirectUrl = `${redirectUrl}${separator}user_id=${encodeURIComponent(externalUserId)}`;
      }

      // Countdown timer
      const countdownInterval = setInterval(() => {
        setCountdown(prev => {
          if (prev <= 1) {
            clearInterval(countdownInterval);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);

      // Redirect after 5 seconds
      const redirectTimer = setTimeout(() => {
        window.location.href = redirectUrl;
      }, 5000);

      return () => {
        clearTimeout(redirectTimer);
        clearInterval(countdownInterval);
      };
    }
  }, [completeRedirectUrl, externalUserId]);

  return (
    <div className="bg-white rounded-lg shadow-lg p-8 text-center">
      <div className="mb-6">
        <CheckCircleIcon className="w-20 h-20 text-green-500 mx-auto mb-4" />
        <h2 className="text-3xl font-bold text-gray-900 mb-2">
          {isScreenedOut ? 'Thank You' : 'Survey Completed!'}
        </h2>
        <p className="text-lg text-gray-600 mb-4">
          {isScreenedOut ? (
            <>Thank you for your time and interest in <span className="font-semibold">&ldquo;{surveyName}&rdquo;</span></>
          ) : (
            <>Thank you for completing <span className="font-semibold">&ldquo;{surveyName}&rdquo;</span></>
          )}
        </p>
      </div>

      {redirecting ? (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
          <h3 className="text-lg font-semibold text-blue-800 mb-2">Redirecting...</h3>
          <p className="text-sm text-blue-700">
            You will be redirected in {countdown} second{countdown !== 1 ? 's' : ''}
          </p>
        </div>
      ) : (
        <div className="bg-green-50 border border-green-200 rounded-lg p-6 mb-6">
          <h3 className="text-lg font-semibold text-green-800 mb-2">
            {isScreenedOut ? 'Thank you for your participation' : 'What happens next?'}
          </h3>
          {isScreenedOut ? (
            <p className="text-sm text-green-700">
              Unfortunately, you do not meet the criteria for this particular survey. We appreciate your time and interest.
            </p>
          ) : (
            <ul className="text-sm text-green-700 text-left space-y-2">
              <li>• Your responses have been successfully submitted</li>
              <li>• Our team will review your submission</li>
              <li>• You may be contacted if additional information is needed</li>
              <li>• Thank you for your valuable participation!</li>
            </ul>
          )}
        </div>
      )}

      {!redirecting && (
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
      )}
    </div>
  );
}