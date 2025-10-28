"use client";

import { useState } from "react";
import { CheckIcon } from "@heroicons/react/24/solid";
import type { SurveyQuestion } from "@/types/survey";

interface MultipleChoiceQuestionProps {
  question: SurveyQuestion;
  onSubmit: (data: any) => void;
  loading: boolean;
  surveySlug: string;
}

export default function MultipleChoiceQuestion({ question, onSubmit, loading }: MultipleChoiceQuestionProps) {
  const [selectedOptions, setSelectedOptions] = useState<string[]>([]);
  const [error, setError] = useState('');

  const handleOptionToggle = (option: string) => {
    setSelectedOptions(prev => {
      if (prev.includes(option)) {
        return prev.filter(o => o !== option);
      } else {
        return [...prev, option];
      }
    });

    if (error) setError('');
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Validation
    if (question.required && selectedOptions.length === 0) {
      setError('Please select at least one option');
      return;
    }

    // Submit answer
    onSubmit({
      multiple_choice_answer: selectedOptions
    });
  };

  const handleSkip = () => {
    if (question.required) return;

    onSubmit({
      multiple_choice_answer: []
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
        {question.options.map((option, index) => {
          const isSelected = selectedOptions.includes(option);
          return (
            <label
              key={index}
              className={`flex items-center p-4 border rounded-lg cursor-pointer transition-colors ${
                isSelected
                  ? 'border-[#D01A8A] bg-[#F5E8F0]'
                  : 'border-gray-300 hover:border-gray-400 hover:bg-gray-50'
              }`}
            >
              <div className="relative flex items-center">
                <input
                  type="checkbox"
                  checked={isSelected}
                  onChange={() => handleOptionToggle(option)}
                  className="sr-only"
                  disabled={loading}
                />
                <div
                  className={`w-5 h-5 border-2 rounded flex items-center justify-center transition-colors ${
                    isSelected
                      ? 'border-[#D01A8A] bg-[#D01A8A]'
                      : 'border-gray-300'
                  }`}
                >
                  {isSelected && (
                    <CheckIcon className="w-3 h-3 text-white" />
                  )}
                </div>
              </div>
              <span className="ml-3 text-gray-900 font-medium">{option}</span>
            </label>
          );
        })}
      </div>

      {selectedOptions.length > 0 && (
        <div className="bg-[#F5E8F0] border border-[#F5E8F0] rounded-lg p-4">
          <h4 className="font-medium text-[#4E0036] mb-2">Selected options:</h4>
          <ul className="text-[#4E0036] text-sm">
            {selectedOptions.map((option, index) => (
              <li key={index}>• {option}</li>
            ))}
          </ul>
        </div>
      )}

      {error && (
        <p className="text-red-500 text-sm">{error}</p>
      )}

      <div className="flex gap-4">
        {!question.required && (
          <button
            type="button"
            onClick={handleSkip}
            disabled={loading}
            className="px-6 py-3 border border-gray-300 rounded-lg text-gray-700 font-medium hover:bg-gray-50 focus:ring-2 focus:ring-[#D01A8A] disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Skip
          </button>
        )}

        <button
          type="submit"
          disabled={loading || (question.required && selectedOptions.length === 0)}
          className={`flex-1 py-3 px-6 rounded-lg text-white font-medium transition-colors ${
            loading || (question.required && selectedOptions.length === 0)
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