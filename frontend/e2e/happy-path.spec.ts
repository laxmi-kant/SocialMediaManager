import { test, expect } from "@playwright/test"

test.describe("Happy Path E2E", () => {
  const email = `e2e-${Date.now()}@test.com`
  const password = "TestPass123!"
  const name = "E2E Test User"

  test("register, login, and navigate dashboard", async ({ page }) => {
    // Register
    await page.goto("/register")
    await page.fill('input[type="email"]', email)
    await page.fill('input[type="password"]', password)
    await page.fill('input[placeholder*="name" i], input[name="full_name"]', name)
    await page.click('button[type="submit"]')

    // Should redirect to login or dashboard
    await page.waitForURL(/\/(login|$)/)

    // Login if redirected to login page
    if (page.url().includes("/login")) {
      await page.fill('input[type="email"]', email)
      await page.fill('input[type="password"]', password)
      await page.click('button[type="submit"]')
    }

    // Should be on dashboard
    await page.waitForURL("/")
    await expect(page.locator("text=Dashboard")).toBeVisible()
  })

  test("navigate to content page", async ({ page }) => {
    // Login first
    await page.goto("/login")
    await page.fill('input[type="email"]', email)
    await page.fill('input[type="password"]', password)
    await page.click('button[type="submit"]')
    await page.waitForURL("/")

    // Navigate to Content
    await page.click('a[href="/content"]')
    await page.waitForURL("/content")
    await expect(page.locator("text=Content")).toBeVisible()
  })

  test("navigate to posts page", async ({ page }) => {
    await page.goto("/login")
    await page.fill('input[type="email"]', email)
    await page.fill('input[type="password"]', password)
    await page.click('button[type="submit"]')
    await page.waitForURL("/")

    await page.click('a[href="/posts"]')
    await page.waitForURL("/posts")
    await expect(page.locator("text=Posts")).toBeVisible()
  })

  test("navigate to leads page", async ({ page }) => {
    await page.goto("/login")
    await page.fill('input[type="email"]', email)
    await page.fill('input[type="password"]', password)
    await page.click('button[type="submit"]')
    await page.waitForURL("/")

    await page.click('a[href="/leads"]')
    await page.waitForURL("/leads")
    await expect(page.locator("text=Leads")).toBeVisible()
  })

  test("health check endpoint", async ({ request }) => {
    const backendUrl = process.env.BACKEND_URL || "http://localhost:8000"
    const resp = await request.get(`${backendUrl}/health`)
    expect(resp.ok()).toBeTruthy()
    const body = await resp.json()
    expect(body.status).toBe("healthy")
  })
})
