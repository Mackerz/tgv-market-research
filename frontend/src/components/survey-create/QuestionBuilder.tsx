import {
  TrashIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  ChevronDownIcon,
  ChevronRightIcon
} from '@heroicons/react/24/outline';
import { Question, QuestionMedia, RoutingRule } from './types';
import { questionTypes } from './constants';
import OptionsEditor from './OptionsEditor';
import MediaEditor from './MediaEditor';
import RoutingRuleEditor from './RoutingRuleEditor';

interface QuestionBuilderProps {
  question: Question;
  index: number;
  total: number;
  expanded: boolean;
  onToggleExpand: () => void;
  onUpdate: (updates: Partial<Question>) => void;
  onRemove: () => void;
  onMoveUp: () => void;
  onMoveDown: () => void;
  onAddOption: () => void;
  onUpdateOption: (optionIndex: number, value: string) => void;
  onRemoveOption: (optionIndex: number) => void;
  onAddRoutingRule: () => void;
  onUpdateRoutingRule: (ruleIndex: number, updates: Partial<RoutingRule>) => void;
  onRemoveRoutingRule: (ruleIndex: number) => void;
  onAddMedia: () => void;
  onUpdateMedia: (mediaIndex: number, updates: Partial<QuestionMedia>) => void;
  onRemoveMedia: (mediaIndex: number) => void;
  allQuestions: Question[];
}

export default function QuestionBuilder({
  question,
  index,
  total,
  expanded,
  onToggleExpand,
  onUpdate,
  onRemove,
  onMoveUp,
  onMoveDown,
  onAddOption,
  onUpdateOption,
  onRemoveOption,
  onAddRoutingRule,
  onUpdateRoutingRule,
  onRemoveRoutingRule,
  onAddMedia,
  onUpdateMedia,
  onRemoveMedia,
  allQuestions
}: QuestionBuilderProps) {
  const needsOptions = question.question_type === 'single' || question.question_type === 'multi';

  return (
    <div className="border rounded-lg">
      {/* Question Header */}
      <div className="p-4 bg-gray-50 flex justify-between items-center border-b">
        <div className="flex items-center space-x-3 flex-1">
          <button
            type="button"
            onClick={onToggleExpand}
            className="text-gray-600 hover:text-gray-900"
          >
            {expanded ? (
              <ChevronDownIcon className="h-5 w-5" />
            ) : (
              <ChevronRightIcon className="h-5 w-5" />
            )}
          </button>
          <span className="font-medium text-gray-900">
            Question {index + 1}: {question.question || '(Untitled)'}
          </span>
        </div>
        <div className="flex items-center space-x-2">
          {index > 0 && (
            <button
              type="button"
              onClick={onMoveUp}
              className="p-1 text-gray-600 hover:text-gray-900"
              title="Move up"
            >
              <ArrowUpIcon className="h-5 w-5" />
            </button>
          )}
          {index < total - 1 && (
            <button
              type="button"
              onClick={onMoveDown}
              className="p-1 text-gray-600 hover:text-gray-900"
              title="Move down"
            >
              <ArrowDownIcon className="h-5 w-5" />
            </button>
          )}
          <button
            type="button"
            onClick={onRemove}
            className="p-1 text-red-600 hover:text-red-900"
            title="Remove question"
          >
            <TrashIcon className="h-5 w-5" />
          </button>
        </div>
      </div>

      {/* Question Body */}
      {expanded && (
        <div className="p-4 space-y-4">
          {/* Question ID */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Question ID
            </label>
            <input
              type="text"
              value={question.id}
              onChange={(e) => onUpdate({ id: e.target.value.replace(/[^a-z0-9_]/g, '_') })}
              className="w-full px-3 py-2 border rounded-md text-gray-900 bg-white"
            />
            <p className="text-xs text-gray-500 mt-1">Unique identifier (lowercase, underscores only)</p>
          </div>

          {/* Question Text */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Question Text *
            </label>
            <textarea
              value={question.question}
              onChange={(e) => onUpdate({ question: e.target.value })}
              rows={2}
              className="w-full px-3 py-2 border rounded-md text-gray-900 bg-white placeholder-gray-400"
              placeholder="Enter your question here"
            />
          </div>

          {/* Question Type and Required */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Question Type
              </label>
              <select
                value={question.question_type}
                onChange={(e) => onUpdate({ question_type: e.target.value })}
                className="w-full px-3 py-2 border rounded-md text-gray-900 bg-white"
              >
                {questionTypes.map(type => (
                  <option key={type.value} value={type.value}>{type.label}</option>
                ))}
              </select>
            </div>
            <div className="flex items-center">
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={question.required}
                  onChange={(e) => onUpdate({ required: e.target.checked })}
                  className="rounded border-gray-300"
                />
                <span className="text-sm font-medium text-gray-700">Required</span>
              </label>
            </div>
          </div>

          {/* Options (for single/multi choice) */}
          {needsOptions && (
            <OptionsEditor
              options={question.options || []}
              onAddOption={onAddOption}
              onUpdateOption={onUpdateOption}
              onRemoveOption={onRemoveOption}
            />
          )}

          {/* Media Section */}
          <MediaEditor
            media={question.media || []}
            onAddMedia={onAddMedia}
            onUpdateMedia={onUpdateMedia}
            onRemoveMedia={onRemoveMedia}
          />

          {/* Routing Rules Section */}
          <RoutingRuleEditor
            routingRules={question.routing_rules || []}
            currentQuestion={question}
            allQuestions={allQuestions}
            needsOptions={needsOptions}
            onAddRoutingRule={onAddRoutingRule}
            onUpdateRoutingRule={onUpdateRoutingRule}
            onRemoveRoutingRule={onRemoveRoutingRule}
          />
        </div>
      )}
    </div>
  );
}
