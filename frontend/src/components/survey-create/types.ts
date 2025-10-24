export interface QuestionMedia {
  url: string;
  type: 'photo' | 'video';
  caption?: string;
}

export interface RoutingCondition {
  question_id: string;
  operator: string;
  value?: string | string[] | number;
}

export interface RoutingRule {
  conditions: RoutingCondition[];
  action: string;
  target_question_id?: string;
}

export interface Question {
  id: string;
  question: string;
  question_type: string;
  required: boolean;
  options?: string[];
  routing_rules?: RoutingRule[];
  media?: QuestionMedia[];
}
