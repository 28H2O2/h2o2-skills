# FDU booking page patterns

These patterns were verified on `booking.fudan.edu.cn` in July–August 2026. Treat them as hints and re-inspect the DOM because the site can change.

## Calendar structure

- The left time axis has historically been `dl.left_time` with `dd.resource_item_info` rows.
- Each date has historically been a `dl.reservation_data`.
- Its `dt.week_header` contains the date and weekday.
- Its `dd.resource_item_info` cells correspond in order to the time-axis rows.
- Available cells have historically included classes such as `green pointer can_active`.
- Full cells have historically included `red` and `no_active` classes.

Locate the date column by its header text. Read the current time-label array, find the requested label, then inspect the same-index cell in the date column. Verify the cell text and interactable state before clicking.

Do not select an element merely because its text says `可预约`: several dates and times can have identical text.

## Capacity semantics

- Parse `(n/m)` as `n` already reserved out of total capacity `m`.
- Remaining capacity is `m - n`.
- `可预约 (14/15)` means one court remains.
- `约满 (15/15)` means no court remains.
- `已过期` and `未开放` are not bookable regardless of a displayed count.

Do not assume the denominator is always 15; parse the live page.

## Duplicate check and verification

- The navigation item has historically displayed `我的预约`.
- A valid record contains the resource name, target date, target time, and a status such as `已预约` or `待签到`.
- Ignore records marked `已取消`.
- A successful submission has historically navigated to `myReservation` and shown `预约成功`, but confirm the matching record when practical.

## Form controls

- The phone input has historically used placeholder `请输入手机号`.
- The submit button displays `确认预约` and has historically included class `confirm_pc_bt`.

If ordinary assignment does not update framework state, set the value through the browser's native input setter and dispatch `input` and `change` events.

## Known pitfalls

- Availability can change between reading and clicking; recheck immediately before selection.
- Matching by text alone can click the wrong date or time.
- A click response is not proof of booking success.
- A local-port connection error can indicate sandbox isolation rather than missing browser authorization.
- Never close a tab that this run did not create.
