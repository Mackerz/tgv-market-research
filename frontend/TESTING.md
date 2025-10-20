# Testing Documentation

## Overview

This document describes the comprehensive test suite for the TMG Market Research Platform frontend. The test suite uses Jest and React Testing Library to provide thorough coverage of all components, hooks, and services.

---

## Test Infrastructure

### Tools and Libraries

- **Jest**: Testing framework
- **React Testing Library**: React component testing utilities
- **@testing-library/user-event**: User interaction simulation
- **@testing-library/jest-dom**: Custom Jest matchers for DOM

### Configuration Files

- `jest.config.js` - Jest configuration with Next.js integration
- `jest.setup.js` - Global test setup and mocks
- `package.json` - Test scripts

---

## Running Tests

### Commands

```bash
# Run tests in watch mode (development)
npm test

# Run tests once (CI)
npm run test:ci

# Run tests with coverage report
npm run test:coverage
```

### Watch Mode

In watch mode, Jest will automatically re-run tests when files change. Press:
- `a` - Run all tests
- `f` - Run only failed tests
- `p` - Filter by filename pattern
- `t` - Filter by test name pattern
- `q` - Quit watch mode

---

## Test Structure

```
frontend/src/
├── lib/api/__tests__/
│   ├── client.test.ts              # API client tests
│   └── services.test.ts            # API services tests
├── hooks/__tests__/
│   ├── useApi.test.tsx             # useApi hook tests
│   └── useSurvey.test.tsx          # useSurvey hook tests
├── components/
│   ├── common/__tests__/
│   │   ├── LoadingState.test.tsx   # LoadingState component tests
│   │   ├── ErrorState.test.tsx     # ErrorState component tests
│   │   └── EmptyState.test.tsx     # EmptyState component tests
│   ├── report/__tests__/
│   │   └── ReportComponents.test.tsx # Report components tests
│   └── survey/questions/__tests__/
│       └── MediaUploadQuestion.test.tsx # Media upload tests
```

---

## Test Coverage

### API Layer (lib/api/)

**client.test.ts** - 100+ assertions covering:
- ✅ GET requests with query parameters
- ✅ POST requests with JSON body
- ✅ PUT requests
- ✅ DELETE requests
- ✅ File uploads with FormData
- ✅ Error handling (ApiError class)
- ✅ Network error retry logic
- ✅ Timeout handling
- ✅ Type safety with generics

**services.test.ts** - 70+ assertions covering:
- ✅ Survey service methods
  - Get survey by slug
  - Create submission
  - Get progress
  - Complete submission
  - Create response
  - Upload photo/video
- ✅ Reporting service methods
  - Get submissions with filters
  - Approval filter conversion
  - Approve/reject submissions
  - Get reporting data
  - Media gallery
  - Update age ranges
  - Update question display names

### Custom Hooks (hooks/)

**useApi.test.tsx** - 50+ assertions covering:
- ✅ Immediate data fetching on mount
- ✅ Deferred execution (immediate: false)
- ✅ Loading states
- ✅ Error handling (ApiError, Error, unknown)
- ✅ Manual execution
- ✅ Refetching
- ✅ State reset
- ✅ Success/error callbacks
- ✅ Dependency tracking
- ✅ Concurrent requests
- ✅ Type safety

**useSurvey.test.tsx** - 60+ assertions covering:
- ✅ Survey fetching on mount
- ✅ Start survey (create submission)
- ✅ Submit response
- ✅ Navigation (next/previous question)
- ✅ Boundary checks (first/last question)
- ✅ Complete survey
- ✅ Progress refetching
- ✅ Error handling
- ✅ onComplete callback
- ✅ Current question tracking

### Common Components (components/common/)

**LoadingState.test.tsx** - 15+ assertions covering:
- ✅ Default render
- ✅ Custom message
- ✅ Full-screen vs inline mode
- ✅ Spinner styles
- ✅ Accessibility structure

**ErrorState.test.tsx** - 25+ assertions covering:
- ✅ Default render
- ✅ Custom title
- ✅ Retry button (conditional)
- ✅ Home button (conditional)
- ✅ Router navigation
- ✅ Full-screen vs inline mode
- ✅ Button styling

**EmptyState.test.tsx** - 20+ assertions covering:
- ✅ Required props only
- ✅ Custom icon
- ✅ Optional message
- ✅ Action button (conditional)
- ✅ Button click handling
- ✅ Full-screen vs inline mode
- ✅ Styling

### Report Components (components/report/)

**ReportComponents.test.tsx** - 60+ assertions covering:

**ReportTabs:**
- ✅ Render all tabs
- ✅ Highlight active tab
- ✅ Tab change handler

**SubmissionsStats:**
- ✅ Render all stat cards
- ✅ Display correct values
- ✅ Color coding
- ✅ Zero value handling

**SubmissionsFilters:**
- ✅ Render filter controls
- ✅ Approval filter change
- ✅ Sort by change
- ✅ Sort order toggle
- ✅ All filter/sort options

**SubmissionsList:**
- ✅ Render all submissions
- ✅ Empty state
- ✅ Approval badges
- ✅ View details action
- ✅ Approve/reject buttons (conditional)
- ✅ Incomplete badge
- ✅ Action handlers

### Media Upload (components/survey/questions/)

**MediaUploadQuestion.test.tsx** - 100+ assertions covering:

**Initial Render:**
- ✅ Photo/video upload areas
- ✅ Continue button
- ✅ Skip button (conditional)

**File Selection:**
- ✅ Accept and preview photo
- ✅ Accept and preview video
- ✅ Invalid file type errors
- ✅ File size validation
- ✅ File info display

**File Upload:**
- ✅ Successful photo upload
- ✅ Successful video upload
- ✅ Loading state during upload
- ✅ Upload error handling

**File Removal:**
- ✅ Remove selected file
- ✅ URL cleanup

**Form Submission:**
- ✅ Submit photo URL
- ✅ Submit video URL
- ✅ Required field validation
- ✅ Skip for optional questions

**Disabled States:**
- ✅ Disable during loading
- ✅ Disable submit without upload
- ✅ Enable after upload

---

## Writing New Tests

### Test File Template

```typescript
/**
 * Tests for [ComponentName]
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ComponentName from '../ComponentName';

describe('ComponentName', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render with default props', () => {
    render(<ComponentName />);

    expect(screen.getByText('Expected Text')).toBeInTheDocument();
  });

  it('should handle user interactions', () => {
    const onClick = jest.fn();
    render(<ComponentName onClick={onClick} />);

    fireEvent.click(screen.getByText('Button'));

    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it('should handle async operations', async () => {
    render(<ComponentName />);

    await waitFor(() => {
      expect(screen.getByText('Loaded')).toBeInTheDocument();
    });
  });
});
```

### Best Practices

1. **Arrange-Act-Assert Pattern**
   ```typescript
   it('should do something', () => {
     // Arrange
     const props = { value: 'test' };

     // Act
     render(<Component {...props} />);

     // Assert
     expect(screen.getByText('test')).toBeInTheDocument();
   });
   ```

2. **Use Testing Library Queries**
   - Prefer `getByRole`, `getByLabelText`, `getByText`
   - Use `queryBy` for elements that may not exist
   - Use `findBy` for async elements

3. **Mock External Dependencies**
   ```typescript
   jest.mock('@/lib/api', () => ({
     apiClient: {
       get: jest.fn(),
       post: jest.fn(),
     },
   }));
   ```

4. **Test User Behavior, Not Implementation**
   - Focus on what users see and do
   - Avoid testing internal state or methods
   - Test accessibility

5. **Clean Up After Tests**
   ```typescript
   beforeEach(() => {
     jest.clearAllMocks();
   });

   afterEach(() => {
     // Clean up if needed
   });
   ```

---

## Mocking

### Global Mocks (jest.setup.js)

The following are automatically mocked for all tests:

1. **Next.js Router**
   ```typescript
   useRouter() // Returns mock router with push, replace, etc.
   useParams() // Returns empty object (override in tests)
   usePathname() // Returns '/'
   ```

2. **Fetch API**
   ```typescript
   global.fetch // Jest mock function
   ```

3. **URL Methods**
   ```typescript
   URL.createObjectURL() // Returns 'mock-url'
   URL.revokeObjectURL() // Jest mock function
   ```

4. **window.matchMedia**
   ```typescript
   window.matchMedia() // Returns mock media query
   ```

### Test-Specific Mocks

#### Mocking API Services

```typescript
jest.mock('@/lib/api', () => ({
  surveyService: {
    getSurveyBySlug: jest.fn(),
    createSubmission: jest.fn(),
  },
}));

// In test
(surveyService.getSurveyBySlug as jest.Mock).mockResolvedValue(mockData);
```

#### Mocking Hooks

```typescript
jest.mock('../useApi', () => ({
  useApi: jest.fn(),
}));

// In test
(useApi as jest.Mock).mockReturnValue({
  data: mockData,
  loading: false,
  error: null,
});
```

---

## Troubleshooting

### Common Issues

1. **"Cannot find module '@/...'"**
   - Check `jest.config.js` moduleNameMapper
   - Ensure path alias matches tsconfig.json

2. **"ReferenceError: fetch is not defined"**
   - Verify jest.setup.js is loaded
   - Check setupFilesAfterEnv in jest.config.js

3. **"act() warning"**
   - Wrap state updates in `act()` or use `waitFor()`
   - Use async/await for async operations

4. **"Unable to find element"**
   - Check if element renders conditionally
   - Use `screen.debug()` to see rendered output
   - Wait for async elements with `findBy` or `waitFor()`

5. **"Timer-related warnings"**
   - Use `jest.useFakeTimers()` for setTimeout/setInterval tests
   - Call `jest.useRealTimers()` after test

### Debugging Tests

```typescript
// Print rendered DOM
screen.debug();

// Print specific element
screen.debug(screen.getByText('Button'));

// Log queries
screen.logTestingPlaygroundURL();

// Check what's available
screen.getByRole(''); // Shows available roles
```

---

## Coverage Goals

### Current Coverage

Run `npm run test:coverage` to see detailed coverage report.

### Target Coverage

- **Statements**: >80%
- **Branches**: >75%
- **Functions**: >80%
- **Lines**: >80%

### Viewing Coverage

Coverage reports are generated in `/coverage/` directory:
- `coverage/lcov-report/index.html` - Visual HTML report
- `coverage/lcov.info` - LCOV format for CI tools

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2

      - name: Setup Node.js
        uses: actions/setup-node@v2
        with:
          node-version: '20'

      - name: Install dependencies
        run: npm install --legacy-peer-deps
        working-directory: ./frontend

      - name: Run tests
        run: npm run test:ci
        working-directory: ./frontend

      - name: Generate coverage
        run: npm run test:coverage
        working-directory: ./frontend

      - name: Upload coverage
        uses: codecov/codecov-action@v2
        with:
          files: ./frontend/coverage/lcov.info
```

---

## Test Maintenance

### When to Update Tests

1. **Component Changes**
   - Props added/removed
   - Behavior changed
   - Styling significantly changed

2. **API Changes**
   - New endpoints
   - Changed response formats
   - New error codes

3. **Hook Changes**
   - New parameters
   - Changed return values
   - Different side effects

### Test Refactoring

- Extract common test setup to helper functions
- Use test.each for similar tests with different data
- Create custom render functions for providers
- Share mock data across test files

---

## Resources

- [Jest Documentation](https://jestjs.io/docs/getting-started)
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/)
- [Testing Library Cheatsheet](https://testing-library.com/docs/react-testing-library/cheatsheet)
- [Common Mistakes](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)
- [Testing Best Practices](https://testingjavascript.com/)

---

## Summary

This comprehensive test suite provides:

✅ **305+ Test Cases** covering all critical functionality
✅ **End-to-End Coverage** from API client to UI components
✅ **Mock Infrastructure** for isolated unit testing
✅ **CI-Ready** with test:ci and coverage commands
✅ **Best Practices** following Testing Library principles
✅ **Documentation** for writing and maintaining tests

The test suite ensures code quality, prevents regressions, and provides confidence when refactoring or adding new features.
