"use client";

import MediaUploadQuestion from './MediaUploadQuestion';
import type { SurveyQuestion } from '@/types';

interface VideoQuestionProps {
  question: SurveyQuestion;
  onSubmit: (data: any) => void;
  loading: boolean;
  surveySlug: string;
}

/**
 * VideoQuestion Component
 * Wrapper around MediaUploadQuestion for video uploads
 */
export default function VideoQuestion({ question, onSubmit, loading, surveySlug }: VideoQuestionProps) {
  return (
    <MediaUploadQuestion
      question={question}
      onSubmit={onSubmit}
      loading={loading}
      surveySlug={surveySlug}
      mediaType="video"
    />
  );
}
