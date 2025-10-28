import { TrashIcon } from '@heroicons/react/24/outline';

interface OptionsEditorProps {
  options: string[];
  onAddOption: () => void;
  onUpdateOption: (index: number, value: string) => void;
  onRemoveOption: (index: number) => void;
}

export default function OptionsEditor({
  options,
  onAddOption,
  onUpdateOption,
  onRemoveOption
}: OptionsEditorProps) {
  return (
    <div>
      <div className="flex justify-between items-center mb-2">
        <label className="block text-sm font-medium text-gray-700">
          Answer Options
        </label>
        <button
          type="button"
          onClick={onAddOption}
          className="text-sm text-[#D01A8A] hover:text-[#4E0036]"
        >
          + Add Option
        </button>
      </div>
      <div className="space-y-2">
        {options.map((option, optIndex) => (
          <div key={optIndex} className="flex items-center space-x-2">
            <input
              type="text"
              value={option}
              onChange={(e) => onUpdateOption(optIndex, e.target.value)}
              placeholder={`Option ${optIndex + 1}`}
              className="flex-1 px-3 py-2 border rounded-md text-gray-900 bg-white placeholder-gray-400"
            />
            <button
              type="button"
              onClick={() => onRemoveOption(optIndex)}
              className="p-2 text-red-600 hover:text-red-900"
            >
              <TrashIcon className="h-4 w-4" />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
