import { TrashIcon } from '@heroicons/react/24/outline';
import { Question, RoutingRule } from './types';
import { operators, routingActions } from './constants';

interface RoutingRuleEditorProps {
  routingRules: RoutingRule[];
  currentQuestion: Question;
  allQuestions: Question[];
  needsOptions: boolean;
  onAddRoutingRule: () => void;
  onUpdateRoutingRule: (index: number, updates: Partial<RoutingRule>) => void;
  onRemoveRoutingRule: (index: number) => void;
}

export default function RoutingRuleEditor({
  routingRules,
  currentQuestion,
  allQuestions,
  needsOptions,
  onAddRoutingRule,
  onUpdateRoutingRule,
  onRemoveRoutingRule
}: RoutingRuleEditorProps) {
  return (
    <div>
      <div className="flex justify-between items-start mb-2">
        <div className="flex-1">
          <label className="block text-sm font-medium text-gray-700">
            Routing Rules (Optional)
          </label>
          <p className="text-xs text-gray-500 mt-1">
            Multiple rules are evaluated in order (OR logic). First matching rule wins.
          </p>
        </div>
        <button
          type="button"
          onClick={onAddRoutingRule}
          className="text-sm text-blue-600 hover:text-blue-800 whitespace-nowrap"
        >
          + Add Routing Rule
        </button>
      </div>
      {routingRules.length > 0 && (
        <div className="space-y-3">
          {routingRules.map((rule, ruleIndex) => (
            <div key={ruleIndex} className="border rounded-md p-3 bg-gray-50 space-y-2">
              <div className="flex justify-between items-start">
                <span className="text-sm font-medium text-gray-700">Rule {ruleIndex + 1}</span>
                <button
                  type="button"
                  onClick={() => onRemoveRoutingRule(ruleIndex)}
                  className="text-red-600 hover:text-red-900"
                >
                  <TrashIcon className="h-4 w-4" />
                </button>
              </div>

              {/* Condition */}
              <div className="grid grid-cols-3 gap-2">
                <div>
                  <label className="block text-xs text-gray-600 mb-1">Operator</label>
                  <select
                    value={rule.conditions[0]?.operator || 'equals'}
                    onChange={(e) => {
                      const newConditions = [...rule.conditions];
                      newConditions[0] = {
                        question_id: newConditions[0]?.question_id || currentQuestion.id,
                        operator: e.target.value,
                        value: newConditions[0]?.value
                      };
                      onUpdateRoutingRule(ruleIndex, { conditions: newConditions });
                    }}
                    className="w-full px-2 py-1 border rounded text-sm text-gray-900 bg-white"
                  >
                    {operators.map(op => (
                      <option key={op.value} value={op.value}>{op.label}</option>
                    ))}
                  </select>
                </div>
                <div className="col-span-2">
                  <label className="block text-xs text-gray-600 mb-1">Value</label>
                  {needsOptions ? (
                    <select
                      value={rule.conditions[0]?.value as string || ''}
                      onChange={(e) => {
                        const newConditions = [...rule.conditions];
                        newConditions[0] = {
                          question_id: newConditions[0]?.question_id || currentQuestion.id,
                          operator: newConditions[0]?.operator || 'equals',
                          value: e.target.value
                        };
                        onUpdateRoutingRule(ruleIndex, { conditions: newConditions });
                      }}
                      className="w-full px-2 py-1 border rounded text-sm text-gray-900 bg-white"
                    >
                      <option value="">Select an option</option>
                      {currentQuestion.options?.map((opt, i) => (
                        <option key={i} value={opt}>{opt}</option>
                      ))}
                    </select>
                  ) : (
                    <input
                      type="text"
                      value={rule.conditions[0]?.value as string || ''}
                      onChange={(e) => {
                        const newConditions = [...rule.conditions];
                        newConditions[0] = {
                          question_id: newConditions[0]?.question_id || currentQuestion.id,
                          operator: newConditions[0]?.operator || 'equals',
                          value: e.target.value
                        };
                        onUpdateRoutingRule(ruleIndex, { conditions: newConditions });
                      }}
                      placeholder="Condition value"
                      className="w-full px-2 py-1 border rounded text-sm text-gray-900 bg-white placeholder-gray-400"
                    />
                  )}
                </div>
              </div>

              {/* Action */}
              <div>
                <label className="block text-xs text-gray-600 mb-1">Action</label>
                <select
                  value={rule.action}
                  onChange={(e) => onUpdateRoutingRule(ruleIndex, { action: e.target.value })}
                  className="w-full px-2 py-1 border rounded text-sm text-gray-900 bg-white"
                >
                  {routingActions.map(action => (
                    <option key={action.value} value={action.value}>{action.label}</option>
                  ))}
                </select>
              </div>

              {/* Target Question (if goto_question) */}
              {rule.action === 'goto_question' && (
                <div>
                  <label className="block text-xs text-gray-600 mb-1">Target Question</label>
                  <select
                    value={rule.target_question_id || ''}
                    onChange={(e) => onUpdateRoutingRule(ruleIndex, { target_question_id: e.target.value })}
                    className="w-full px-2 py-1 border rounded text-sm text-gray-900 bg-white"
                  >
                    <option value="">Select a question</option>
                    {allQuestions.map((q, i) => (
                      <option key={i} value={q.id}>
                        {q.id} - {q.question || '(Untitled)'}
                      </option>
                    ))}
                  </select>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
