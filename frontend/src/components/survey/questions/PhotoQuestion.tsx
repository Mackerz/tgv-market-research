"use client";

import MediaUploadQuestion from './MediaUploadQuestion';
import type { SurveyQuestion } from '@/types';

interface PhotoQuestionProps {
  question: SurveyQuestion;
  onSubmit: (data: any) => void;
  loading: boolean;
  surveySlug: string;
}

/**
 * PhotoQuestion Component
 * Wrapper around MediaUploadQuestion for photo uploads
 */
export default function PhotoQuestion({ question, onSubmit, loading, surveySlug }: PhotoQuestionProps) {
  return (
    <MediaUploadQuestion
      question={question}
      onSubmit={onSubmit}
      loading={loading}
      surveySlug={surveySlug}
      mediaType="photo"
    />
  );
}
