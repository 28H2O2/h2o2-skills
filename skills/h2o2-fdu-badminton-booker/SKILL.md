---
name: h2o2-fdu-badminton-booker
description: Configure one-shot checks, recurring monitoring, and explicitly authorized auto-booking for Fudan University badminton courts through the user's logged-in Chrome or Edge session, with duplicate protection and optional Feishu notifications. Use when a user asks to inspect FDU badminton availability, watch specified dates or slots, receive vacancy alerts, submit one bounded reservation, change the polling interval or deadline, test notifications, or inspect booking state on booking.fudan.edu.cn. Recurring monitoring requires a host with an automation-management tool; browser operation requires the separately installed web-access skill.
---

# H2O2 FDU Badminton Booker

Operate the FDU booking page through the user's existing browser login. Keep every check and booking within the exact scope the user authorized.

## 1. Select a supported mode

Determine the host capabilities before promising background work:

- `one-shot-check`: Inspect current availability once. This works in any compatible agent that can load `web-access`.
- `recurring-monitor`: Recheck on a schedule and notify on availability. Require an automation-management tool.
- `auto-book`: Recheck and submit one authorized reservation when a permitted slot becomes available. Require an automation-management tool for recurring operation.

Search the available tools for automation management. In Codex Desktop, use a heartbeat automation attached to the current task. If no automation tool exists, do not substitute a shell loop, `cron`, detached process, or claim that monitoring is active. Offer a one-shot check or explain that recurring operation needs Codex Desktop or another host with equivalent recurring-task support.

## 2. Verify dependencies before network access

Load and follow the separately installed `web-access` skill completely. It may appear as `web-access:web-access` in a namespaced client. This skill supplies the booking policy; `web-access` supplies the browser driver.

If `web-access` is missing, stop before opening the site or creating an automation. Tell the user to install it from its upstream repository:

```bash
npx skills add eze-is/web-access
```

For Claude Code, its plugin installation is also supported:

```bash
claude plugin marketplace add https://github.com/eze-is/web-access
claude plugin install web-access@web-access --scope user
```

Do not install the dependency without user approval. Do not replace it with unauthenticated fetching or an isolated headless browser unless the user explicitly accepts losing their existing login state.

Require Node.js 22 or newer. Resolve the installed `web-access` directory instead of assuming a machine-specific path. Run its `scripts/check-deps.mjs` with `--browser chrome` or `--browser edge`. Follow its remote-debugging, browser-risk-notice, and temporary-tab rules.

## 3. Collect the operating contract

Before preflight, resolve:

- mode: `one-shot-check`, `recurring-monitor`, or `auto-book`;
- browser: Chrome or Edge;
- booking URL and venue; use `https://booking.fudan.edu.cn/reservation/fe/site/reservationInfo?id=1055` only after the user confirms it is the intended venue;
- target date and exact permitted slot(s), including priority order;
- polling interval and stop time for recurring modes; recommend 10 minutes unless latency matters more;
- notification channel: native task updates, optionally plus Feishu;
- for auto-book only: booking phone number, permission to select and click `确认预约` once, and whether an existing matching valid reservation counts as success.

Summarize the contract once. Ask for confirmation only when auto-book authorization is not already explicit. Authorization never covers cancellation, another date or slot, or repeated submission.

Treat phone numbers and webhooks as secrets. Never bake either into this skill or repeat them in user-visible output.

### Optional Feishu setup

Native task notification is sufficient by default. If the user requests Feishu, use `scripts/feishu_notify.py` so the webhook stays in an owner-only local config file rather than the automation prompt.

1. Resolve this skill's absolute directory.
2. Ask the user to run `python3 <SKILL_DIR>/scripts/feishu_notify.py configure` in their terminal. Do not ask them to paste the webhook into chat when avoidable.
3. Run `python3 <SKILL_DIR>/scripts/feishu_notify.py check`.
4. If requested, run `python3 <SKILL_DIR>/scripts/feishu_notify.py test` and require a successful Feishu response.
5. Put only the absolute helper path and optional config-file path in the automation prompt, never the webhook URL.

If secure local configuration is unavailable, fall back to native notifications unless the user explicitly accepts another storage method.

## 4. Run preflight

1. Create a private temporary background tab through `web-access`; never reuse or close a user tab.
2. Load the confirmed booking URL with the selected browser's logged-in session.
3. Confirm the expected venue and date/time grid are present.
4. Read [references/fudan-page-patterns.md](references/fudan-page-patterns.md) and inspect the live DOM. Treat stored patterns as hints, not guarantees.
5. Inspect `我的预约` when auto-booking or when the user asks for booking state.
6. Close the temporary tab after preflight.

If login, CAPTCHA, risk control, or an unexpected page blocks inspection, report the precise blocker. Do not create an automation that has not passed preflight.

Do not ask the user to re-enable remote debugging merely because a sandbox cannot reach a local port. First distinguish sandbox isolation from a browser authorization failure and use the host's approved local connection path when available.

## 5. Interpret and recheck availability

Map time labels and date-column cells from the DOM on every run. Never rely on screenshot coordinates or a previously observed fixed index.

- Parse `(n/m)` as `n` already reserved out of capacity `m`; remaining capacity is `m - n`.
- `可预约` with `n < m`: available.
- `约满` or `n >= m`: unavailable.
- `已过期` and `未开放`: unavailable regardless of counts.

Re-read the target cell immediately before selection because availability can change between inspection and click.

## 6. Submit safely in auto-book mode

1. Inspect `我的预约` for a valid, non-cancelled record matching the exact date and a permitted slot.
2. If one exists, do not submit again. Count it as success only if the operating contract allows that.
3. Return to the booking page and recheck availability.
4. Select only the highest-priority currently available permitted slot.
5. Verify or fill the authorized phone number.
6. Click `确认预约` exactly once.
7. Confirm success from an explicit success message or a matching valid record in `我的预约`; a click alone is not success.
8. Record the actual date, slot, court when known, timestamp, and confirmation evidence.

Never retry an uncertain submission, cancel a reservation, or book a second slot after success.

## 7. Create and retire recurring automation

Prefer updating a matching existing automation over creating a duplicate. Read [references/automation-template.md](references/automation-template.md), replace every placeholder, remove unused branches, and put the complete operating contract into the automation prompt. Do not rely on conversational context that a later run may not have.

Keep healthy full-state checks quiet unless the user requested status reports. On confirmed success, notify the task and configured Feishu channel, then delete or disable the automation. On CAPTCHA, expired login, risk control, system failure, submission failure, or an uncertain result, stop submitting, notify with the required user action, and disable further booking attempts. At the deadline, delete or disable the automation and close its temporary tab.

After monitoring ends, remind the user they may disable browser remote debugging if they no longer need it.
