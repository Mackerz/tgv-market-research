export const questionTypes = [
  { value: 'single', label: 'Single Choice' },
  { value: 'multi', label: 'Multiple Choice' },
  { value: 'free_text', label: 'Free Text' },
  { value: 'photo', label: 'Photo Upload' },
  { value: 'video', label: 'Video Upload' }
];

export const operators = [
  { value: 'equals', label: 'Equals' },
  { value: 'not_equals', label: 'Not Equals' },
  { value: 'contains', label: 'Contains' },
  { value: 'not_contains', label: 'Not Contains' },
  { value: 'contains_any', label: 'Contains Any' },
  { value: 'contains_all', label: 'Contains All' },
  { value: 'greater_than', label: 'Greater Than' },
  { value: 'less_than', label: 'Less Than' },
  { value: 'is_answered', label: 'Is Answered' },
  { value: 'is_not_answered', label: 'Is Not Answered' }
];

export const routingActions = [
  { value: 'continue', label: 'Continue to Next Question' },
  { value: 'goto_question', label: 'Go to Specific Question' },
  { value: 'end_survey', label: 'End Survey' }
];
