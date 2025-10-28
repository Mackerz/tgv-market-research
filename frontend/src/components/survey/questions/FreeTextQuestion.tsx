"use client";

import { useState } from "react";
import type { SurveyQuestion } from "@/types/survey";

interface FreeTextQuestionProps {
  question: SurveyQuestion;
  onSubmit: (data: any) => void;
  loading: boolean;
  surveySlug: string;
}

export default function FreeTextQuestion({ question, onSubmit, loading }: FreeTextQuestionProps) {
  const [answer, setAnswer] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Validation
    if (question.required && !answer.trim()) {
      setError('This question is required');
      return;
    }

    if (answer.trim().length > 2000) {
      setError('Answer must be less than 2000 characters');
      return;
    }

    // Submit answer
    onSubmit({
      free_text_answer: answer.trim()
    });
  };

  const handleSkip = () => {
    if (question.required) return;

    onSubmit({
      free_text_answer: ''
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <textarea
          value={answer}
          onChange={(e) => {
            setAnswer(e.target.value);
            if (error) setError('');
          }}
          placeholder="Type your answer here..."
          rows={6}
          className={`w-full px-4 py-3 border rounded-lg text-gray-900 resize-none focus:ring-2 focus:ring-[#D01A8A] focus:border-transparent ${
            error ? 'border-red-500' : 'border-gray-300'
          }`}
          disabled={loading}
          maxLength={2000}
        />
        <div className="flex justify-between items-center mt-2">
          {error && <p className="text-red-500 text-sm">{error}</p>}
          <p className="text-gray-500 text-sm ml-auto">
            {answer.length}/2000 characters
          </p>
        </div>
      </div>

      <div className="flex flex-col sm:flex-row gap-3 sm:gap-4">
        {!question.required && (
          <button
            type="button"
            onClick={handleSkip}
            disabled={loading}
            className="px-6 py-3 border border-gray-300 rounded-lg text-gray-700 font-medium hover:bg-gray-50 focus:ring-2 focus:ring-[#D01A8A] disabled:opacity-50 disabled:cursor-not-allowed touch-manipulation"
          >
            Skip
          </button>
        )}

        <button
          type="submit"
          disabled={loading || (question.required && !answer.trim())}
          className={`flex-1 py-3 px-6 rounded-lg text-white font-medium transition-colors touch-manipulation ${
            loading || (question.required && !answer.trim())
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-[#D01A8A] hover:bg-[#B0156E] focus:ring-2 focus:ring-[#D01A8A]'
          }`}
        >
          {loading ? (
            <div className="flex items-center justify-center">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
              Submitting...
            </div>
          ) : (
            'Continue'
          )}
        </button>
      </div>
    </form>
  );
}