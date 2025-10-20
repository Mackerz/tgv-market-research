# Frontend Code Review - TMG Market Research

**Date**: October 20, 2025
**Focus**: DRY, SOLID Principles, Project Structure
**Status**: Critical Issues Identified

---

## Executive Summary

The frontend codebase has several critical issues that violate DRY and SOLID principles. The most significant problem is a **1,234-line monolithic report page** that handles multiple responsibilities. Additionally, there's substantial code duplication across question components and missing architectural patterns.

### Severity Levels
- 🔴 **Critical**: Major violations, significant technical debt
- 🟡 **Medium**: Important improvements needed
- 🟢 **Minor**: Nice-to-have improvements

---

## 1. Critical Issues (🔴)

### Issue #1: Monolithic Report Page (1,234 lines)
**File**: `src/app/report/[reportSlug]/page.tsx`
**Severity**: 🔴 Critical
**Violation**: Single Responsibility Principle (SOLID)

The report page is a massive component that handles:
- Submissions list management
- Submission detail view
- Approval/rejection workflow
- Reporting data with charts
- Media gallery
- Settings management (age ranges, question display names)
- Multiple API calls and state management
- Complex filtering and sorting logic

**Impact**:
- Impossible to test individual features
- High cognitive load for developers
- Difficult to maintain and debug
- Cannot reuse any of these features
- Performance issues (re-renders entire component)

**Recommendation**: Split into **at least 6 separate components**:
```
src/features/reporting/
├── components/
│   ├── SubmissionsList.tsx
│   ├── SubmissionDetail.tsx
│   ├── ApprovalControls.tsx
│   ├── ReportingCharts.tsx
│   ├── MediaGalleryTab.tsx
│   └── SettingsTab.tsx
├── hooks/
│   ├── useSubmissions.ts
│   ├── useReportingData.ts
│   └── useSettings.ts
└── types/
    └── reporting.ts
```

---

### Issue #2: Duplicate Media Upload Logic
**Files**:
- `src/components/survey/questions/PhotoQuestion.tsx` (243 lines)
- `src/components/survey/questions/VideoQuestion.tsx` (similar structure)

**Severity**: 🔴 Critical
**Violation**: DRY Principle

**Duplicate Code** (~200 lines):
```typescript
// Both components have identical:
1. File selection logic
2. File validation (different limits)
3. Preview URL management
4. Upload state management
5. FormData creation
6. API upload logic
7. Error handling
8. UI for file preview and removal
9. Submit/Skip button logic
```

**Differences** (only these vary):
- File type validation (`image/*` vs `video/*`)
- File size limit (10MB vs 100MB)
- Upload endpoint (`/upload/photo` vs `/upload/video`)
- Icon component (PhotoIcon vs VideoCameraIcon)
- Preview component (img vs video tag)

**Recommendation**: Create a generic `MediaUploadQuestion` component:

```typescript
// src/components/survey/questions/MediaUploadQuestion.tsx
interface MediaUploadConfig {
  type: 'photo' | 'video';
  accept: string;
  maxSize: number;
  uploadEndpoint: string;
  icon: React.ComponentType;
  previewComponent: React.ComponentType<{url: string}>;
}

export default function MediaUploadQuestion({
  question,
  onSubmit,
  loading,
  surveySlug,
  config
}: MediaUploadQuestionProps) {
  // Shared upload logic
}
```

**Impact**: Eliminates ~150 lines of duplicate code

---

### Issue #3: No Type Definitions File
**Severity**: 🔴 Critical
**Violation**: DRY Principle

**Problem**: Same interfaces duplicated across multiple files:

```typescript
// Duplicated in 3+ files:
interface Survey {
  id: number;
  survey_slug: string;
  name: string;
  survey_flow: SurveyQuestion[];
  is_active: boolean;
}

interface SurveyQuestion {
  id: string;
  question: string;
  question_type: 'free_text' | 'single' | 'multi' | 'photo' | 'video';
  required: boolean;
  options?: string[];
}

// And many more...
```

**Files with duplicate types**:
- `src/app/survey/[slug]/page.tsx`
- `src/components/survey/QuestionComponent.tsx`
- `src/components/survey/questions/*.tsx`
- `src/app/report/[reportSlug]/page.tsx`

**Recommendation**: Create centralized type definitions:

```typescript
// src/types/survey.ts
export interface Survey { ... }
export interface SurveyQuestion { ... }
export interface Submission { ... }
export interface Response { ... }

// src/types/reporting.ts
export interface ReportingData { ... }
export interface ChartData { ... }

// src/types/media.ts
export interface MediaAnalysis { ... }
```

**Impact**: Eliminates 100+ lines of duplicate type definitions

---

### Issue #4: Inline API Calls (No API Layer)
**Severity**: 🔴 Critical
**Violation**: Single Responsibility Principle, Open/Closed Principle

**Problem**: API calls scattered throughout components:

```typescript
// Every component does this:
const response = await fetch(apiUrl(`/api/surveys/${id}`));
const data = await response.json();
if (!response.ok) { ... }
```

**Issues**:
1. Cannot mock API calls for testing
2. Cannot add authentication easily
3. Cannot add retry logic
4. Cannot add request/response interceptors
5. Error handling duplicated everywhere
6. Cannot track API usage

**Recommendation**: Create API service layer:

```typescript
// src/lib/api/client.ts
export class ApiClient {
  async get<T>(endpoint: string): Promise<T> { ... }
  async post<T>(endpoint: string, data: any): Promise<T> { ... }
  // Centralized error handling, retries, etc.
}

// src/lib/api/services/surveys.ts
export const surveyService = {
  getSurvey: (slug: string) => apiClient.get<Survey>(`/api/surveys/slug/${slug}`),
  createSubmission: (slug: string, data: any) => apiClient.post(`/api/surveys/${slug}/submit`, data),
};
```

---

## 2. Medium Issues (🟡)

### Issue #5: No Custom Hooks for Shared Logic
**Severity**: 🟡 Medium
**Violation**: DRY Principle

**Problem**: State management patterns repeated across pages:

```typescript
// Repeated in multiple components:
const [loading, setLoading] = useState(true);
const [error, setError] = useState<string | null>(null);
const [data, setData] = useState<T | null>(null);

useEffect(() => {
  fetchData();
}, [dependency]);

const fetchData = async () => {
  try {
    setLoading(true);
    const response = await fetch(...);
    setData(await response.json());
  } catch (error) {
    setError(error.message);
  } finally {
    setLoading(false);
  }
};
```

**Recommendation**: Create custom hooks:

```typescript
// src/hooks/useApi.ts
export function useApi<T>(fetcher: () => Promise<T>, deps: any[]) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchData();
  }, deps);

  return { data, loading, error, refetch };
}

// Usage:
const { data: survey, loading, error } = useApi(
  () => surveyService.getSurvey(slug),
  [slug]
);
```

---

### Issue #6: No Form Validation Library
**Severity**: 🟡 Medium
**Violation**: DRY Principle

**Problem**: `PersonalInfoForm.tsx` has 50+ lines of manual validation:

```typescript
const validateForm = () => {
  const newErrors: Record<string, string> = {};

  // Email validation
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!formData.email) {
    newErrors.email = 'Email is required';
  } else if (!emailRegex.test(formData.email)) {
    newErrors.email = 'Please enter a valid email address';
  }

  // More validation...
  return Object.keys(newErrors).length === 0;
};
```

**Recommendation**: Use a form validation library (React Hook Form + Zod):

```typescript
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';

const schema = z.object({
  email: z.string().email('Please enter a valid email'),
  phone_number: z.string().min(7).max(15),
  region: z.string().min(1, 'Please select your region'),
  date_of_birth: z.date().max(new Date()),
  gender: z.string().min(1, 'Please select your gender'),
});

const { register, handleSubmit, formState: { errors } } = useForm({
  resolver: zodResolver(schema)
});
```

**Benefits**:
- Declarative validation
- Type-safe
- Built-in error handling
- Performance optimized

---

### Issue #7: No Loading/Error Components
**Severity**: 🟡 Medium
**Violation**: DRY Principle

**Problem**: Loading and error states duplicated everywhere:

```typescript
// Repeated in every page:
if (loading) {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
        <p className="text-gray-600">Loading...</p>
      </div>
    </div>
  );
}

if (error) {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <div className="text-6xl mb-4">❌</div>
        <h1 className="text-2xl font-bold">Error</h1>
        <p>{error}</p>
      </div>
    </div>
  );
}
```

**Recommendation**: Create reusable state components:

```typescript
// src/components/common/LoadingState.tsx
export function LoadingState({ message = 'Loading...' }) { ... }

// src/components/common/ErrorState.tsx
export function ErrorState({ error, onRetry }) { ... }

// src/components/common/EmptyState.tsx
export function EmptyState({ message, icon, action }) { ... }

// Usage:
if (loading) return <LoadingState />;
if (error) return <ErrorState error={error} onRetry={fetchData} />;
if (!data) return <EmptyState message="No surveys found" />;
```

---

### Issue #8: Hardcoded Data
**Severity**: 🟡 Medium
**Violation**: Open/Closed Principle

**Problem**: Regions, genders, and other options hardcoded in components:

```typescript
// In PersonalInfoForm.tsx:
const regions = [
  { code: 'UK', name: 'United Kingdom', prefix: '+44', flag: '🇬🇧' },
  { code: 'US', name: 'United States', prefix: '+1', flag: '🇺🇸' },
  // ... 13 hardcoded regions
];

const genders = ['Male', 'Female', "I'd rather not say"];
```

**Recommendation**: Move to configuration files:

```typescript
// src/config/form-options.ts
export const REGIONS = [...];
export const GENDERS = [...];

// Or fetch from API:
export const useFormOptions = () => {
  return useApi(() => apiClient.get('/api/form-options'));
};
```

---

## 3. Minor Issues (🟢)

### Issue #9: Inconsistent Component Structure
**Severity**: 🟢 Minor

**Problem**: Components in two different locations:
- `src/app/components/` (1 file)
- `src/components/` (7 files)

**Recommendation**: Consolidate to `src/components/`

---

### Issue #10: No Component Documentation
**Severity**: 🟢 Minor

**Problem**: Components lack JSDoc comments explaining props and usage.

**Recommendation**: Add JSDoc comments:

```typescript
/**
 * Displays a survey question with appropriate input based on type
 * @param {SurveyQuestion} question - The question to display
 * @param {Function} onSubmit - Callback when answer is submitted
 * @param {boolean} loading - Whether submission is in progress
 * @param {string} surveySlug - Unique identifier for the survey
 */
export default function QuestionComponent({ ... }) { ... }
```

---

### Issue #11: Debug Code in Production
**Severity**: 🟢 Minor

**Problem**: `src/app/survey/[slug]/page.tsx` line 189-192:

```typescript
{/* Debug Info */}
<div className="mb-4 p-2 bg-gray-100 text-xs">
  Debug: Step={currentStep}, SubmissionID={submissionId}, Progress={progress?.current_question}/{progress?.total_questions}
  <br />Survey: {survey ? 'loaded' : 'null'}, Progress obj: {progress ? JSON.stringify(progress) : 'null'}
</div>
```

**Recommendation**: Remove or wrap in `process.env.NODE_ENV === 'development'`

---

## 4. Proposed Improved Folder Structure

### Current Structure (Problems)
```
src/
├── app/                      # Mixed concerns
│   ├── components/           # Only 1 component
│   ├── survey/[slug]/        # Business logic in page
│   └── report/[reportSlug]/  # 1,234-line monster
├── components/               # Some shared components
│   └── survey/
└── config/                   # Only API config
```

### Proposed Structure (Feature-Based)
```
src/
├── app/                                    # Next.js pages only
│   ├── survey/[slug]/
│   │   └── page.tsx                       # ~50 lines, orchestration only
│   ├── report/[reportSlug]/
│   │   └── page.tsx                       # ~50 lines, orchestration only
│   └── layout.tsx
│
├── features/                               # Feature modules
│   ├── survey/
│   │   ├── components/
│   │   │   ├── PersonalInfoForm.tsx
│   │   │   ├── QuestionRenderer.tsx
│   │   │   ├── SurveyProgress.tsx
│   │   │   └── questions/
│   │   │       ├── MediaUploadQuestion.tsx  # Generic for photo/video
│   │   │       ├── FreeTextQuestion.tsx
│   │   │       ├── SingleChoiceQuestion.tsx
│   │   │       └── MultipleChoiceQuestion.tsx
│   │   ├── hooks/
│   │   │   ├── useSurvey.ts
│   │   │   ├── useSubmission.ts
│   │   │   └── useSurveyProgress.ts
│   │   └── types/
│   │       └── survey.ts
│   │
│   ├── reporting/
│   │   ├── components/
│   │   │   ├── SubmissionsList/
│   │   │   │   ├── index.tsx
│   │   │   │   ├── SubmissionRow.tsx
│   │   │   │   └── SubmissionFilters.tsx
│   │   │   ├── SubmissionDetail/
│   │   │   │   ├── index.tsx
│   │   │   │   ├── ApprovalControls.tsx
│   │   │   │   └── ResponsesList.tsx
│   │   │   ├── ReportingCharts/
│   │   │   │   ├── index.tsx
│   │   │   │   ├── DemographicsChart.tsx
│   │   │   │   └── QuestionChart.tsx
│   │   │   ├── MediaGallery/
│   │   │   │   ├── index.tsx
│   │   │   │   ├── MediaGrid.tsx
│   │   │   │   └── MediaFilters.tsx
│   │   │   └── Settings/
│   │   │       ├── index.tsx
│   │   │       ├── AgeRangeSettings.tsx
│   │   │       └── QuestionNameSettings.tsx
│   │   ├── hooks/
│   │   │   ├── useSubmissions.ts
│   │   │   ├── useReportingData.ts
│   │   │   ├── useMediaGallery.ts
│   │   │   └── useReportSettings.ts
│   │   └── types/
│   │       └── reporting.ts
│   │
│   └── media/
│       ├── components/
│       │   ├── MediaPlayer.tsx
│       │   └── MediaUploader.tsx
│       ├── hooks/
│       │   └── useMediaUpload.ts
│       └── types/
│           └── media.ts
│
├── components/                              # Shared/common components
│   ├── ui/                                  # UI primitives
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Select.tsx
│   │   ├── Modal.tsx
│   │   └── Card.tsx
│   ├── layout/
│   │   ├── PageHeader.tsx
│   │   ├── PageContainer.tsx
│   │   └── Sidebar.tsx
│   └── feedback/
│       ├── LoadingState.tsx
│       ├── ErrorState.tsx
│       ├── EmptyState.tsx
│       └── Toast.tsx
│
├── lib/                                     # Utilities and services
│   ├── api/
│   │   ├── client.ts                       # HTTP client
│   │   ├── services/
│   │   │   ├── surveys.ts
│   │   │   ├── submissions.ts
│   │   │   ├── reporting.ts
│   │   │   └── media.ts
│   │   └── types/
│   │       └── api.ts
│   ├── utils/
│   │   ├── validation.ts
│   │   ├── formatting.ts
│   │   └── date.ts
│   └── constants/
│       ├── api-endpoints.ts
│       └── form-options.ts
│
├── hooks/                                   # Global hooks
│   ├── useApi.ts
│   ├── useDebounce.ts
│   └── useLocalStorage.ts
│
├── types/                                   # Global TypeScript types
│   ├── index.ts
│   └── common.ts
│
└── config/
    ├── api.ts
    └── app.ts
```

---

## 5. Refactoring Priority

### Phase 1: Foundation (High Priority)
1. **Create type definitions** - Eliminate duplicate interfaces (1 day)
2. **Create API service layer** - Centralize API calls (2 days)
3. **Extract common components** - LoadingState, ErrorState, etc. (1 day)

### Phase 2: Major Refactors (Medium Priority)
4. **Split report page** - Break into 6+ components (3 days)
5. **Create generic MediaUploadQuestion** - Eliminate photo/video duplication (1 day)
6. **Create custom hooks** - useApi, useSurvey, etc. (2 days)

### Phase 3: Polish (Lower Priority)
7. **Add form validation library** - React Hook Form + Zod (1 day)
8. **Move to feature-based structure** - Reorganize folders (2 days)
9. **Add component documentation** - JSDoc comments (1 day)
10. **Remove debug code** - Clean up production code (0.5 day)

**Total Estimated Time**: 13.5 days

---

## 6. Code Quality Metrics

### Before Refactoring
| Metric | Value | Status |
|--------|-------|--------|
| Largest Component | 1,234 lines | 🔴 Critical |
| Duplicate Code | ~300 lines | 🔴 Critical |
| Duplicate Types | ~100 lines | 🔴 Critical |
| Components > 300 lines | 3 components | 🔴 Critical |
| Inline API calls | 20+ instances | 🔴 Critical |
| Manual validation | 50+ lines | 🟡 Medium |
| Debug code in prod | Yes | 🟢 Minor |

### After Refactoring (Estimated)
| Metric | Target | Improvement |
|--------|--------|-------------|
| Largest Component | <200 lines | 84% reduction |
| Duplicate Code | 0 lines | 100% elimination |
| Duplicate Types | 0 lines | 100% elimination |
| Components > 300 lines | 0 components | 100% improvement |
| Inline API calls | 0 instances | 100% elimination |
| Manual validation | 0 lines | 100% elimination |
| Debug code in prod | No | Fixed |

---

## 7. Benefits of Refactoring

### Developer Experience
- ✅ Easier to find and modify code
- ✅ Faster onboarding for new developers
- ✅ Reduced cognitive load
- ✅ Better IDE autocomplete and navigation

### Code Quality
- ✅ Testable components (can write unit tests)
- ✅ Reusable components across features
- ✅ Type-safe with centralized types
- ✅ Consistent error handling

### Performance
- ✅ Smaller bundle sizes (code splitting)
- ✅ Faster re-renders (smaller components)
- ✅ Better tree-shaking

### Maintainability
- ✅ Changes isolated to feature modules
- ✅ Easy to add new features
- ✅ Clear separation of concerns
- ✅ Follows industry best practices

---

## 8. Immediate Action Items

### Critical (Do First)
1. Create `src/types/` directory with shared interfaces
2. Create `src/lib/api/client.ts` with HTTP client
3. Split report page into separate components

### Important (Do Next)
4. Create generic MediaUploadQuestion component
5. Create custom hooks (useApi, useSurvey)
6. Add form validation library

### Nice to Have (Do Later)
7. Reorganize to feature-based structure
8. Add JSDoc documentation
9. Remove debug code

---

## Conclusion

The frontend codebase has significant technical debt, particularly:
- **1,234-line report page** (should be ~50 lines)
- **~300 lines of duplicate code** across components
- **No architectural patterns** (API layer, custom hooks, etc.)

Following the recommended refactoring will result in:
- **~400 lines eliminated** through DRY principles
- **84% reduction** in largest component size
- **100% testable** components
- **Industry-standard** architecture

The refactoring is estimated at **13.5 days** and should be prioritized as **Phase 2** after the backend refactoring is complete.
