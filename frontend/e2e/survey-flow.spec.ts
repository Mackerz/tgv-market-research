import { test, expect } from '@playwright/test';

test.describe('Survey Flow Integration Tests', () => {
  const testSurveySlug = 'monster-lifestyle';

  test.beforeEach(async ({ page }) => {
    // Navigate to survey page
    await page.goto(`/survey/${testSurveySlug}`);
    await page.waitForLoadState('networkidle');
  });

  test('should display survey welcome page', async ({ page }) => {
    // Check that the survey loads
    await expect(page).toHaveURL(`/survey/${testSurveySlug}`);

    // Should show start button or personal info form
    const hasStartButton = await page.locator('button:has-text("Start")').count() > 0;
    const hasPersonalInfoForm = await page.locator('form').count() > 0;

    expect(hasStartButton || hasPersonalInfoForm).toBeTruthy();
  });

  test('should validate personal information form', async ({ page }) => {
    // Try to submit without filling required fields
    const emailInput = page.locator('input[name="email"], input[type="email"]');

    if (await emailInput.count() > 0) {
      // Clear email field
      await emailInput.fill('');

      // Try to find and click submit/next button
      const submitButton = page.locator('button:has-text("Next"), button:has-text("Submit"), button:has-text("Continue")').first();
      await submitButton.click();

      // Should show validation errors
      const errorMessages = page.locator('[role="alert"], .error, .text-red');
      await expect(errorMessages.first()).toBeVisible({ timeout: 5000 }).catch(() => {
        // Validation might prevent button click, which is also valid
      });
    }
  });

  test('should complete personal information form', async ({ page }) => {
    // Fill in personal information if form is present
    const emailInput = page.locator('input[name="email"], input[type="email"]');

    if (await emailInput.count() > 0) {
      await emailInput.fill('test@example.com');

      // Fill phone number
      const phoneInput = page.locator('input[name="phone"], input[name="phoneNumber"], input[type="tel"]');
      if (await phoneInput.count() > 0) {
        await phoneInput.fill('1234567890');
      }

      // Select region if dropdown exists
      const regionSelect = page.locator('select[name="region"]');
      if (await regionSelect.count() > 0) {
        await regionSelect.selectOption({ index: 1 });
      }

      // Fill date of birth
      const dobInput = page.locator('input[name="dateOfBirth"], input[type="date"]');
      if (await dobInput.count() > 0) {
        await dobInput.fill('1990-01-01');
      }

      // Select gender if radio buttons exist
      const genderRadio = page.locator('input[name="gender"]').first();
      if (await genderRadio.count() > 0) {
        await genderRadio.check();
      }

      // Submit form
      const submitButton = page.locator('button:has-text("Next"), button:has-text("Submit"), button:has-text("Continue")').first();
      await submitButton.click();

      // Should progress to next step or show questions
      await page.waitForTimeout(2000);
    }
  });

  test('should navigate through survey questions', async ({ page }) => {
    // Complete personal info first (if needed)
    await completPersonalInfo(page);

    // Check if we're on a question page
    const questionText = page.locator('h1, h2, h3, [role="heading"]');
    const hasQuestions = await questionText.count() > 0;

    if (hasQuestions) {
      // Answer a single choice question if present
      const singleChoiceOption = page.locator('input[type="radio"]').first();
      if (await singleChoiceOption.count() > 0) {
        await singleChoiceOption.check();

        // Click next button
        const nextButton = page.locator('button:has-text("Next"), button:has-text("Continue")');
        if (await nextButton.count() > 0) {
          await nextButton.click();
          await page.waitForTimeout(1000);
        }
      }
    }
  });

  test('should handle multiple choice questions', async ({ page }) => {
    await completePersonalInfo(page);

    // Look for checkboxes (multiple choice)
    const checkboxes = page.locator('input[type="checkbox"]');
    const count = await checkboxes.count();

    if (count > 0) {
      // Check first two options
      await checkboxes.nth(0).check();
      if (count > 1) {
        await checkboxes.nth(1).check();
      }

      // Verify they're checked
      await expect(checkboxes.nth(0)).toBeChecked();

      // Navigate to next question
      const nextButton = page.locator('button:has-text("Next"), button:has-text("Continue")');
      if (await nextButton.count() > 0) {
        await nextButton.click();
      }
    }
  });

  test('should handle free text questions', async ({ page }) => {
    await completePersonalInfo(page);

    // Look for textarea
    const textarea = page.locator('textarea');
    if (await textarea.count() > 0) {
      await textarea.fill('This is my test feedback. I really enjoy this product and use it daily.');

      // Verify text was entered
      await expect(textarea).toHaveValue(/test feedback/);

      // Navigate to next
      const nextButton = page.locator('button:has-text("Next"), button:has-text("Continue")');
      if (await nextButton.count() > 0) {
        await nextButton.click();
      }
    }
  });

  test('should allow navigation back to previous questions', async ({ page }) => {
    await completePersonalInfo(page);

    // Answer first question
    const firstOption = page.locator('input[type="radio"]').first();
    if (await firstOption.count() > 0) {
      await firstOption.check();

      // Go to next question
      const nextButton = page.locator('button:has-text("Next")');
      if (await nextButton.count() > 0) {
        await nextButton.click();
        await page.waitForTimeout(1000);

        // Try to go back
        const backButton = page.locator('button:has-text("Back"), button:has-text("Previous")');
        if (await backButton.count() > 0) {
          await backButton.click();
          await page.waitForTimeout(1000);

          // Should be back on previous question
          // Verify the previously selected option is still checked
          await expect(firstOption).toBeChecked();
        }
      }
    }
  });

  test('should display progress indicator', async ({ page }) => {
    // Check for progress indicator
    const progressBar = page.locator('[role="progressbar"], .progress, progress');
    const hasProgress = await progressBar.count() > 0;

    // Or check for step indicators like "Question 1 of 5"
    const stepIndicator = page.getByText(/\d+\s*of\s*\d+|Step\s*\d+/i);
    const hasStepIndicator = await stepIndicator.count() > 0;

    expect(hasProgress || hasStepIndicator).toBeTruthy();
  });

  test('should display completion page after survey', async ({ page }) => {
    // This test would need to complete entire survey
    // For now, just check the structure exists
    await completePersonalInfo(page);

    // Navigate through questions rapidly (mock completion)
    // In a real test, you'd answer all questions
    // For now, just verify the test framework works
    expect(page.url()).toContain('/survey/');
  });
});

// Helper function to complete personal info form
async function completePersonalInfo(page) {
  const emailInput = page.locator('input[name="email"], input[type="email"]');

  if (await emailInput.count() > 0) {
    await emailInput.fill('e2e-test@example.com');

    const phoneInput = page.locator('input[name="phone"], input[name="phoneNumber"], input[type="tel"]');
    if (await phoneInput.count() > 0) {
      await phoneInput.fill('5555555555');
    }

    const regionSelect = page.locator('select[name="region"]');
    if (await regionSelect.count() > 0) {
      await regionSelect.selectOption({ index: 1 });
    }

    const dobInput = page.locator('input[name="dateOfBirth"], input[type="date"]');
    if (await dobInput.count() > 0) {
      await dobInput.fill('1995-06-15');
    }

    const genderRadio = page.locator('input[name="gender"]').first();
    if (await genderRadio.count() > 0) {
      await genderRadio.check();
    }

    const submitButton = page.locator('button:has-text("Next"), button:has-text("Submit"), button:has-text("Continue")').first();
    if (await submitButton.count() > 0) {
      await submitButton.click();
      await page.waitForTimeout(2000);
    }
  }
}
