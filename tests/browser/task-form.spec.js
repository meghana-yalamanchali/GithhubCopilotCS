const { test, expect } = require('@playwright/test');

function localFutureDate() {
    const date = new Date();
    date.setDate(date.getDate() + 2);
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${date.getFullYear()}-${month}-${day}`;
}

async function signIn(page) {
    await page.goto('/signup');
    await page.locator('input[name="username"]').fill('browser-user');
    await page.locator('input[name="password"]').fill('browser-password');
    await page.getByRole('button').click();
    await page.locator('input[name="username"]').fill('browser-user');
    await page.locator('input[name="password"]').fill('browser-password');
    await page.getByRole('button').click();
    await expect(page).toHaveURL(/\/$/);
}

test.beforeEach(async ({ page }) => {
    await signIn(page);
});

test('blocks blank submission with accessible field errors and task-name focus', async ({ page }) => {
    let addTaskRequests = 0;
    page.on('request', request => {
        if (request.method() === 'POST' && new URL(request.url()).pathname === '/') {
            addTaskRequests += 1;
        }
    });

    await page.getByRole('button', { name: '+' }).click();

    await expect(page.locator('#new-item-error')).toHaveText('Enter a task name.');
    await expect(page.locator('#due-date-error')).toHaveText('Enter a due date.');
    await expect(page.locator('#new-item')).toHaveAttribute('aria-invalid', 'true');
    await expect(page.locator('#new-item')).toHaveAttribute('aria-describedby', 'new-item-error');
    await expect(page.locator('#due-date')).toHaveAttribute('aria-describedby', 'due-date-error');
    await expect(page.locator('#new-item-error')).toHaveAttribute('role', 'alert');
    await expect(page.locator('#new-item')).toBeFocused();
    await expect.poll(() => addTaskRequests).toBe(0);
});

test('marks only the missing due date invalid and focuses it', async ({ page }) => {
    await page.locator('#new-item').fill('Write acceptance tests');
    await page.getByRole('button', { name: '+' }).click();

    await expect(page.locator('#new-item-error')).toHaveText('');
    await expect(page.locator('#new-item')).not.toHaveAttribute('aria-invalid');
    await expect(page.locator('#due-date-error')).toHaveText('Enter a due date.');
    await expect(page.locator('#due-date')).toBeFocused();
});

test('clears corrected field state on a later invalid submission', async ({ page }) => {
    await page.getByRole('button', { name: '+' }).click();
    await page.locator('#new-item').fill('Corrected task');
    await page.getByRole('button', { name: '+' }).click();

    await expect(page.locator('#new-item-error')).toHaveText('');
    await expect(page.locator('#new-item')).not.toHaveAttribute('aria-invalid');
    await expect(page.locator('#new-item')).not.toHaveAttribute('aria-describedby');
    await expect(page.locator('#due-date-error')).toHaveText('Enter a due date.');
});

test('allows a valid submission to use the existing POST flow', async ({ page }) => {
    await page.locator('#new-item').fill('Browser future task');
    await page.locator('#due-date').fill(localFutureDate());
    await page.getByRole('button', { name: '+' }).click();

    await expect(page).toHaveURL(/\/$/);
    await expect(page.locator('.task_name')).toContainText('Browser future task');
});

test('keeps inline errors within a narrow viewport', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.getByRole('button', { name: '+' }).click();

    await expect(page.locator('#new-item-error')).toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
});