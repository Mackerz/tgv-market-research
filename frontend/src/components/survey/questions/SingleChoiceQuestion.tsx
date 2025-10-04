"use client";

import { useState } from "react";

interface SurveyQuestion {
  id: string;
  question: string;
  question_type: string;
  required: boolean;
  options?: string[];
}

interface SingleChoiceQuestionProps {
  question: SurveyQuestion;
  onSubmit: (data: any) => void;
  loading: boolean;
  surveySlug: string;
}

export default function SingleChoiceQuestion({ question, onSubmit, loading }: SingleChoiceQuestionProps) {
  const [selectedOption, setSelectedOption] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Validation
    if (question.required && !selectedOption) {
      setError('Please select an option');
      return;
    }

    // Submit answer
    onSubmit({
      single_answer: selectedOption
    });
  };

  const handleSkip = () => {
    if (question.required) return;

    onSubmit({
      single_answer: ''
    });
  };

  if (!question.options || question.options.length === 0) {
    return (
      <div className="text-center text-red-600 p-8">
        <p>No options available for this question</p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="space-y-3">
        {question.options.map((option, index) => (
          <label
            key={index}
            className={`flex items-center p-4 border rounded-lg cursor-pointer transition-colors touch-manipulation ${
              selectedOption === option
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-300 hover:border-gray-400 hover:bg-gray-50'
            }`}
          >
            <input
              type="radio"
              name="single_choice"
              value={option}
              checked={selectedOption === option}
              onChange={(e) => {
                setSelectedOption(e.target.value);
                if (error) setError('');
              }}
              className="h-5 w-5 sm:h-4 sm:w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
              disabled={loading}
            />
            <span className="ml-3 text-gray-900 font-medium text-base leading-relaxed">{option}</span>
          </label>
        ))}
      </div>

      {error && (
        <p className="text-red-500 text-sm">{error}</p>
      )}

      <div className="flex flex-col sm:flex-row gap-3 sm:gap-4">
        {!question.required && (
          <button
            type="button"
            onClick={handleSkip}
            disabled={loading}
            className="px-6 py-3 border border-gray-300 rounded-lg text-gray-700 font-medium hover:bg-gray-50 focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed touch-manipulation"
          >
            Skip
          </button>
        )}

        <button
          type="submit"
          disabled={loading || (question.required && !selectedOption)}
          className={`flex-1 py-3 px-6 rounded-lg text-white font-medium transition-colors touch-manipulation ${
            loading || (question.required && !selectedOption)
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-700 focus:ring-2 focus:ring-blue-500'
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