# Feedback → Google Sheets

The **Help center** button (speech-bubble "?" icon, top-right of the header) opens a small feedback window.
Each submission lands in a Google Sheet. No server is needed: a tiny Google Apps Script attached to the
sheet receives the form, saves the screenshot to your Google Drive, and adds a row.

Each row contains:

| Column | Example |
|---|---|
| Time | 26/09/2026 10:42 |
| Type | Wrong code |
| Message | the Java version fails for an empty array |
| Page | `/sheet-150/arrays-hashing#lc-1` (open it directly) |
| Section | `LC 1 · Two Sum › Optimized Code — HashMap O(n)` (what was on screen) |
| Selected text | text the reader had highlighted, if any |
| Screenshot | link to the image in your Drive (the visible part of that section) |
| Device | `390×844 · iPhone · dark` |

## Setup (about 5 minutes)

1. **Create the sheet.** Go to [sheets.new](https://sheets.new), name it e.g. `LearnViaNotes Feedback`.
   In row 1 type these headers: `Time | Type | Message | Page | Section | Selected text | Screenshot | Device`.

2. **Add the script.** In the sheet: **Extensions → Apps Script**. Delete what's there and paste:

   ```js
   const FOLDER_NAME = 'LearnViaNotes feedback screenshots'

   function doPost(e) {
     const p = e.parameter
     const clip = (v, n) => String(v || '').slice(0, n)

     let screenshot = ''
     if (p.screenshot && p.screenshot.startsWith('data:image/jpeg;base64,')) {
       const bytes = Utilities.base64Decode(p.screenshot.split(',')[1])
       const blob = Utilities.newBlob(bytes, 'image/jpeg', 'feedback-' + Date.now() + '.jpg')
       screenshot = folder_().createFile(blob).getUrl()
     }

     SpreadsheetApp.getActiveSpreadsheet().getSheets()[0].appendRow([
       new Date(),
       clip(p.type, 50),
       clip(p.message, 2000),
       clip(p.page, 300),
       clip(p.section, 300),
       clip(p.selection, 500),
       screenshot,
       clip(p.device, 200),
     ])
     return ContentService.createTextOutput('ok')
   }

   // Health check: opening the URL in a private window should show "LearnViaNotes feedback: ok".
   function doGet() {
     return ContentService.createTextOutput('LearnViaNotes feedback: ok')
   }

   function folder_() {
     const found = DriveApp.getFoldersByName(FOLDER_NAME)
     return found.hasNext() ? found.next() : DriveApp.createFolder(FOLDER_NAME)
   }
   ```

   Click **Save** (💾).

3. **Publish it.** Click **Deploy → New deployment** → gear icon → **Web app**.
   - Description: `feedback`
   - Execute as: **Me**
   - Who has access: **Anyone**

   Click **Deploy**, then **Authorize access** and allow it (Google shows an "unverified app" warning because
   it's your own script — choose *Advanced → Go to … (unsafe)*). It needs access to this sheet and to
   create screenshot files in your Drive.

4. **Copy the Web app URL** (it looks like `https://script.google.com/macros/s/AKfy…/exec`).

5. **Connect the app.** Open `src/config.ts` and paste it:

   ```ts
   export const FEEDBACK_URL = 'https://script.google.com/macros/s/AKfy…/exec'
   ```

   Rebuild / redeploy the site. The Help center now shows **Send feedback** instead of "Feedback isn't connected yet".

6. **Test it.** Open the Help center on any page and send a message. A new row appears in the sheet
   within a few seconds, and the screenshot appears in the Drive folder *LearnViaNotes feedback screenshots*.

## Troubleshooting: the site says "sent" but no row appears

The browser can't read the script's reply, so the site can't tell when Google rejects a message.
Open the Web app URL in a **private/incognito window**:

- **"LearnViaNotes feedback: ok"** → the script is reachable; check that the sheet has the header row and look at
  *Apps Script → Executions* for errors.
- **A Google sign-in page** → the deployment isn't public. Go to **Deploy → Manage deployments → ✏️ Edit**, set
  **Who has access: Anyone**, choose **Version: New version**, and click **Deploy**. The URL stays the same.
- **"Page not found"** → the deployment was deleted or the URL is wrong. Create a new deployment and paste its URL
  into `src/config.ts`.

## Notes

- If you edit the script later, use **Deploy → Manage deployments → Edit → Version: New version**, so the URL stays the same.
- Optional: in the sheet, **Extensions → Apps Script → Triggers** or **Tools → Notification settings** can email you on every new row.
- The reader can remove the screenshot before sending.
- Spam: the form has a hidden "honeypot" field that silently drops most bots. Messages are limited to 2000 characters.
- The browser can't read Apps Script's reply (it doesn't send CORS headers), so the site shows "Thanks" once the request is sent.
