const { test, expect } = require('@playwright/test');

test('power calculation works', async ({ page }) => {
  await page.goto('http://127.0.0.1:8000/calculations-page');

  await page.selectOption('#operation', 'power');
  await page.fill('#num1', '2');
  await page.fill('#num2', '3');

  await page.click('button');

  await expect(page.locator('#result')).toContainText('8');
});


test('modulus calculation works', async ({ page }) => {
  await page.goto('http://127.0.0.1:8000/calculations-page');

  await page.selectOption('#operation', 'modulus');
  await page.fill('#num1', '10');
  await page.fill('#num2', '3');

  await page.click('button');

  await expect(page.locator('#result')).toContainText('1');
});