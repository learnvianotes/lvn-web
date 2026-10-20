/* The Privacy Policy. Every claim here must match what the code does — change both together. */

import { Link } from 'react-router-dom'
import { APP_NAME, RETENTION } from '@/config'
import { Fact, Mailbox } from './Fact'

export function PrivacyPolicy() {
  return (
    <>
      <p className="lead">
        {APP_NAME} is run by <Fact field="operator" /> (“we”, “us”). This policy explains what personal data we collect,
        why, who processes it for us, how long we keep it and how you can use your rights. It is written for India’s
        Information Technology Act, 2000 and its rules, and the Digital Personal Data Protection Act, 2023.
      </p>

      <h2>The short version</h2>
      <ul>
        <li>You can read every note without an account. Then we store nothing about you on our servers.</li>
        <li>Accounts are for adults (18 or older).</li>
        <li>With an account, we keep your name, email and study data so your progress follows you between devices.</li>
        <li>Google Analytics runs only if you allow it. You can change your mind any time in Settings.</li>
        <li>We don’t sell your data and we don’t show ads.</li>
        <li>You can download your data or delete your account from Settings at any time.</li>
      </ul>

      <h2>Who can have an account</h2>
      <p>
        Accounts are only for people who are 18 or older. When you create an account we ask your date of birth, use it
        once to check your age, and keep only the fact that you confirmed you are 18 or older and when. We don’t store
        your date of birth. If you are under 18 we don’t create the account. If we learn that an account belongs to
        someone under 18, we delete its data at once and the account itself as soon as we can.
      </p>

      <h2>What we collect and why</h2>
      <div className="table-wrap">
        <table>
          <thead>
            <tr><th>What</th><th>When</th><th>Why</th></tr>
          </thead>
          <tbody>
            <tr>
              <td>Name and email address, and your password (held as a secure hash by Firebase Authentication — we never see it). With Google sign-in: the name, email and profile picture Google shares.</td>
              <td>You create an account or sign in</td>
              <td>To sign you in and show whose account it is</td>
            </tr>
            <tr>
              <td>That you confirmed you are 18 or older, when, and which version of the Terms and this policy you accepted</td>
              <td>You create an account, or first sign in after this policy took effect</td>
              <td>To keep accounts to adults and to show what you agreed to</td>
            </tr>
            <tr>
              <td>Study data: topics and problems you mark, your study history (topic, day, time spent, visits), streak, focus-timer minutes, review queue, personal notes and preferences</td>
              <td>You use {APP_NAME} while signed in</td>
              <td>To keep your progress in step across your devices</td>
            </tr>
            <tr>
              <td>Activity events: topics and problems opened, marked and completed, time spent, searches (including the words you searched), read-aloud, study-kit and focus-timer use, and the filters and sorting you choose — with the app version, device type (for example “Android”) and screen width</td>
              <td>You use {APP_NAME} while signed in</td>
              <td>To learn which notes help, and to count anonymous totals per topic (such as “trending” topics)</td>
            </tr>
            <tr>
              <td>A feedback report: your message, the page and section, any text you selected, a screenshot of that section (you can remove it before sending), device and theme, and your email only if you tick “You can email me”</td>
              <td>You send a report from the Help center</td>
              <td>To fix mistakes and, if you asked, reply to you</td>
            </tr>
            <tr>
              <td>Google Analytics: pages viewed, approximate location worked out from your IP address, device and browser, through cookies</td>
              <td>Only after you choose “Allow”</td>
              <td>To count visits and see which pages are used</td>
            </tr>
            <tr>
              <td>Technical data: IP address, browser and the pages requested</td>
              <td>Every visit</td>
              <td>Our hosting provider keeps these in server logs to run and protect the service</td>
            </tr>
          </tbody>
        </table>
      </div>

      <h3>On your device</h3>
      <p>
        So the site works without an account, your browser keeps your progress, preferences, theme and choices (such
        as your analytics choice) in local storage on your device. When you are signed in, Firebase keeps your session
        in the browser’s storage. These are needed for the site to work, so we don’t ask for consent for them. Signing
        out removes your study data from the device.
      </p>

      <h2>What we don’t do</h2>
      <p>
        We don’t sell or rent your personal data, we don’t show ads, and we don’t share your data with anyone for their
        own marketing. We don’t use your data to make decisions about you that have legal or similar effects.
      </p>

      <h2>Who processes your data for us</h2>
      <ul>
        <li>
          <strong>Google (Firebase)</strong> — Authentication (sign-in), Cloud Firestore (your account and study data),
          Hosting (serves the site), Cloud Functions (anonymous topic totals and cleanup after an account is deleted)
          and, only with your consent, Google Analytics.
        </li>
        <li><strong>Google (Sheets and Apps Script)</strong> — receives feedback reports.</li>
        <li>
          <strong>Google Fonts and jsDelivr</strong> — serve the site’s fonts and icons, so they see your IP address
          and browser when your browser downloads them.
        </li>
      </ul>
      <p>
        They process data only to provide these services to us, under their data processing terms. Google may store
        and process data in India and in other countries where it runs data centres. Read-aloud uses your browser’s own
        voices; some browsers send the text being read to their own speech service.
      </p>

      <h2>How long we keep it</h2>
      <ul>
        <li>
          <strong>Account and study data:</strong> until you delete your account. Deleting it removes your data from our
          database straight away; copies in our backups are overwritten within {RETENTION.backupDays} days.
        </li>
        <li><strong>Feedback reports:</strong> up to {RETENTION.feedbackMonths} months, then deleted.</li>
        <li><strong>Google Analytics data:</strong> {RETENTION.analyticsMonths} months.</li>
        <li><strong>Anonymous topic totals:</strong> kept, as they identify no one.</li>
        <li>We may keep a record longer when the law requires it, for example to deal with a legal claim.</li>
      </ul>

      <h2>Your rights</h2>
      <ul>
        <li><strong>See and take your data:</strong> Settings → Your data → Export my data downloads it as a file.</li>
        <li><strong>Correct it:</strong> email us and we will fix wrong or incomplete details.</li>
        <li><strong>Delete it:</strong> Settings → Your data → Delete account, or email us.</li>
        <li>
          <strong>Withdraw consent:</strong> turn Google Analytics off in <Link to="/settings">Settings</Link> (or in
          the banner) at any time; withdrawing is as easy as giving it. Deleting your account withdraws everything else.
        </li>
        <li><strong>Nominate someone</strong> to use these rights for you if you die or can no longer act: email us.</li>
        <li>
          <strong>Complain:</strong> write to our Grievance Officer (below). If you are not satisfied with the answer you
          may complain to the Data Protection Board of India.
        </li>
      </ul>
      <p>We answer requests within the times on the <Link to="/grievance">Grievance Redressal</Link> page.</p>

      <h2>Security</h2>
      <p>
        The site is served only over HTTPS. Passwords are handled by Firebase Authentication and never reach us. Our
        database rules let each account read and write only its own data. No system is perfectly secure; if a breach
        affects your personal data we will tell you and the authorities as the law requires.
      </p>

      <h2>Changes to this policy</h2>
      <p>
        When we change this policy we update the date at the top. If a change affects how we use your data, we will
        tell signed-in users in the app before it applies and, where the law requires, ask for your consent again.
      </p>

      <h2>Contact</h2>
      <dl className="legal-contact">
        <dt>Data fiduciary</dt><dd><Fact field="operator" /></dd>
        <dt>Grievance Officer</dt><dd><Fact field="grievanceOfficer" /></dd>
        <dt>Email</dt><dd><Mailbox /></dd>
        <dt>Address</dt><dd><Fact field="address" /></dd>
      </dl>
    </>
  )
}
