# Heartbeat automation template

Replace every angle-bracket placeholder before creating the automation. Remove every branch that does not apply. Never place a raw webhook URL in this prompt.

```text
Monitor Fudan University badminton availability at <BOOKING_URL> for <TARGET_DATE> and <ALLOWED_SLOTS>.

Use the installed web-access skill and the user's already-authorized <BROWSER: chrome|edge> login session. Resolve the web-access skill directory and run its preflight with `--browser <BROWSER>`. Do not switch browsers because login states may differ. Create a private temporary background tab for each check and close only that tab.

Operating contract:
- Mode: <recurring-monitor|auto-book>
- Venue: <CONFIRMED_VENUE>
- Slot priority: <ORDERED_SLOT_LIST>
- Booking phone source: <AUTHORIZED_PHONE_OR_NOT_APPLICABLE>
- Polling interval: <INTERVAL>
- Deadline: <DEADLINE_WITH_TIMEZONE>
- Existing matching reservation counts as success: <YES|NO|NOT_APPLICABLE>
- Availability notification deduplication: <NOTIFY_ONCE|NOTIFY_ON_CHANGE|CUSTOM>
- Native notification policy: <EVENTS_TO_NOTIFY>
- Feishu helper: <ABSOLUTE_HELPER_PATH|NOT_APPLICABLE>
- Feishu config: <ABSOLUTE_CONFIG_PATH|DEFAULT|NOT_APPLICABLE>

Read current time labels and the target date column from the DOM on every run. Parse `(n/m)` as n already reserved out of capacity m. `可预约` with n < m is available with m - n remaining. `约满`, n >= m, `已过期`, and `未开放` are unavailable.

On every run:
1. Inspect only the allowed date and slots.
2. If none is available, close the temporary tab and finish quietly.
3. In recurring-monitor mode, notify once according to the configured deduplication policy. Never select or submit.
4. In auto-book mode, first inspect `我的预约` for a valid, non-cancelled reservation matching the exact date and any allowed slot. Never submit when one exists. Treat it as success only when the contract permits.
5. Return to the booking page and recheck availability. Select only the highest-priority currently available allowed slot.
6. Verify or fill the authorized phone. Click `确认预约` exactly once. Never retry an uncertain result.
7. Confirm success only from an explicit success response or a matching valid record in `我的预约`.

For Feishu notifications, call:
`python3 <ABSOLUTE_HELPER_PATH> send --text <MESSAGE>`
Add `--config <ABSOLUTE_CONFIG_PATH>` only when a non-default config path is specified. Require exit code 0. Never read, print, or pass the webhook URL directly.

On confirmed success, notify with the title `【复旦羽毛球预约成功】`, actual date, slot, court when known, confirmation evidence, booking-page link, and current Asia/Shanghai time. Notify this task, then delete or disable this automation.

If CAPTCHA, expired login, risk control, system error, submission failure, or an uncertain result occurs, do not submit again. Notify with the title `【复旦羽毛球自动预约失败】`, attempted slot, reason, required user action, and Asia/Shanghai time. Disable further booking attempts and notify this task.

Never book outside <TARGET_DATE> and <ALLOWED_SLOTS>. Never cancel a reservation. Never expose a phone number or webhook in user-visible output.

At <DEADLINE_WITH_TIMEZONE>, delete or disable this automation. If every check remained full and healthy, end quietly.
```
