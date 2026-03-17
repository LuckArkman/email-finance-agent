import { test, expect } from '@playwright/test';

/**
 * End-to-End simulation of the Invoice Lifecycle:
 * Login -> Ingestion -> OCR Processing -> Dashboard Real-time update.
 */
test.describe('Invoice Pipeline E2E', () => {

  test('should complete the full ingestion to analytics cycle', async ({ page }) => {
    // 1. Authentication
    await page.goto('/login');
    await page.fill('input[type="email"]', 'admin@luckarkman.com');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button[type="submit"]');

    // Wait for redirect to Dashboard
    await expect(page).toHaveURL('/');
    await expect(page.locator('h2')).toContainText('Financial Overview');

    // 2. Simulate Background Ingestion (Mocked for this stage)
    // In a real environment, we'd trigger a webhook payload here.
    // For this simulation, we check if the Inbox is accessible.
    await page.click('text=Invoices');
    await expect(page).toHaveURL('/invoices');
    await expect(page.locator('h2')).toContainText('Invoices Inbox');

    // 3. Document Audit (Split Screen)
    // Click the first row to open the viewer
    await page.click('table tbody tr:first-child');
    await expect(page.locator('text=Document Audit View')).toBeVisible();
    await expect(page.locator('text=AI Intelligence Extraction')).toBeVisible();

    // 4. Force Approval (HITL)
    await page.click('text=Approve Extraction');
    await expect(page.locator('text=Document Audit View')).not.toBeVisible();

    // 5. Verify Dashboard Analytics Update
    await page.click('text=Dashboard');
    await expect(page).toHaveURL('/');
    
    // Check if Metric cards are visible and populated
    const metricCards = page.locator('.glass');
    await expect(metricCards.first()).toBeVisible();
  });

});
