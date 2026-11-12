import Link from 'next/link'
import { ACCOUNTS_FROM_AGE, FULL_ACCOUNT_FROM_AGE, RETENTION } from '@/config/legal'
import { ContactList, Fact } from './Fact'
import { LEGAL_DOCUMENTS } from './documents'

/**
 * Privacy Policy — draft for the owner's review (§15.2; India's IT Act 2000 and SPDI Rules 2011, the DPDP Act 2023).
 * Every claim here must match what the apps do: change both together. Numbers come from config/legal.ts.
 */
export function Privacy() {
  return (
    <>
      <p>
        LearnViaNotes is run by <Fact field="operator" /> (“we”, “us”). This policy explains what personal data we collect
        when you use the website and the apps, why, who processes it for us, how long we keep it and how you can use your
        rights. We do not sell your personal data and we do not show you advertising.
      </p>

      <h2>The short version</h2>
      <ul>
        <li>You can read public notes and subjects without an account.</li>
        <li>
          Accounts are for people aged {ACCOUNTS_FROM_AGE} or older. LearnViaNotes is not directed at children under{' '}
          {ACCOUNTS_FROM_AGE}. From {ACCOUNTS_FROM_AGE} until {FULL_ACCOUNT_FROM_AGE}, some features stay limited, and a
          parent or guardian must give verifiable consent, in line with India’s Digital Personal Data Protection Act, 2023.
        </li>
        <li>With an account, we keep your details, your notes and your study activity so LearnViaNotes works for you on every device.</li>
        <li>Google Analytics runs only if you allow it, and you can change your mind at any time.</li>
        <li>You can download all your data or delete your account from your profile page.</li>
      </ul>

      <h2>1. What we collect</h2>
      <ul>
        <li>
          <strong>Account:</strong> your name, email address, handle and age (or date of birth, if you gave one); your password, stored only as a
          secure hash, or the Google account you sign in with.
        </li>
        <li>
          <strong>What you agreed to:</strong> when you registered and which versions of the Terms, this policy and the
          content licence you accepted, and when.
        </li>
        <li>
          <strong>Optional details:</strong> a college or organisation email to verify your account, your department, year
          of study and interests, a profile photo, and for teachers their profile and skills.
        </li>
        <li>
          <strong>Your content:</strong> notes and the files in them, folders, tags, shares and copies; what you post,
          comment and answer in groups and classes; quiz and contest answers; reports you make.
        </li>
        <li>
          <strong>Learning activity events:</strong> what you open, study and revise, for how long, your reviews, focus
          sessions and exam plans — so the app can plan your week and suggest what to study next.
        </li>
        <li>
          <strong>AI features:</strong> the text you ask an AI feature to work on, and its answers.
        </li>
        <li>
          <strong>Technical data:</strong> your sign-in sessions (device and browser), your IP address in security logs, and
          error reports — sent without your name, email, cookies or the query part of addresses.
        </li>
        <li>
          <strong>Google Analytics</strong>, only if you choose “Allow” when we ask: the pages you view (their address
          without its query), your approximate location worked out from your IP address, and your device and browser,
          through cookies.
        </li>
      </ul>

      <h2>2. Why we use it</h2>
      <ul>
        <li>To run your account and show your notes to you and to the people you choose.</li>
        <li>To keep the community safe: moderation, preventing abuse, and keeping accounts to people aged {ACCOUNTS_FROM_AGE} or older.</li>
        <li>To plan your studying and recommend what to learn next, from your own learning activity.</li>
        <li>To fix problems and keep the service secure.</li>
        <li>To send you the emails you need (confirming your address, security notices) and the ones you asked for.</li>
        <li>With your consent, to count visits and see which pages help (Google Analytics).</li>
      </ul>
      <p>We process your data with your consent and, where the law allows, for these legitimate uses.</p>

      <h2>3. Who can have an account</h2>
      <p>
        LearnViaNotes is not directed at children under {ACCOUNTS_FROM_AGE}. Accounts are for people who are{' '}
        {ACCOUNTS_FROM_AGE} or older. We ask your age when you create an account and keep it with your account; it is
        never shown to anyone. From {ACCOUNTS_FROM_AGE} until {FULL_ACCOUNT_FROM_AGE} the account is restricted and some
        features stay off, and you need verifiable consent from a parent or guardian, in line with India’s Digital
        Personal Data Protection Act, 2023. If the age you give is under {ACCOUNTS_FROM_AGE}, we don’t create the account
        and don’t keep the age; if a sign-in with Google had already created it, we delete it straight away. If we learn
        that an account belongs to someone under {ACCOUNTS_FROM_AGE}, we remove it.
      </p>

      <h2>4. Who else sees it</h2>
      <ul>
        <li>The people you share notes with, your groups and classes, and anyone, for what you make public.</li>
        <li>
          Service providers that run parts of LearnViaNotes for us, under contract and only for that:
          <ul>
            <li>Amazon Web Services (Lightsail) — the servers the website and the API run on;</li>
            <li>Cloudflare — R2, where files and backups are stored;</li>
            <li>
              Google — Firebase Authentication for Google sign-in, Firebase Cloud Messaging for push notifications to the
              phone app, and Google Analytics if you allow it;
            </li>
            <li>Resend — the emails we send you;</li>
            <li>Sentry — error reports, sent without your name, email, cookies or the query part of addresses.</li>
          </ul>
        </li>
        <li>
          AI features send only the text needed for the task you asked for — never your name or account details — to the
          provider configured for that task. The providers the service can use are OpenAI, Anthropic and Google (Gemini).
          An administrator may instead use a model we run ourselves, or another service that speaks OpenAI’s API.
        </li>
        <li>Authorities, when the law requires it.</li>
      </ul>

      <h2>5. How long we keep it</h2>
      <ul>
        <li>Your account, notes and files: until you delete them. Deleted notes stay in the trash for {RETENTION.trashDays} days.</li>
        <li>
          When you delete your account, it goes {RETENTION.deletionGraceDays} days after you ask (you can change your mind
          until then). What you made public stays, shown as by “Deleted user”; everything else is deleted. Copies in our
          backups are overwritten within {RETENTION.backupDays} days.
        </li>
        <li>Learning activity events: {RETENTION.learningEventsMonths} months, then only as totals.</li>
        <li>Data exports you download: {RETENTION.exportDays} days.</li>
        <li>Server logs: {RETENTION.logsDays} days. Security and moderation records: up to {RETENTION.auditYears} years.</li>
        <li>Google Analytics data: {RETENTION.analyticsMonths} months.</li>
        <li>We may keep a record longer when the law requires it, for example to deal with a legal claim.</li>
      </ul>

      <h2>6. Your rights</h2>
      <ul>
        <li>
          <strong>See and take your data:</strong> your profile page → Your data → Download your data gives you an archive
          of everything we hold about you: your account with your age (or date of birth, if you gave one) and the terms you accepted, your notes and
          files, your posts and comments, your study progress and every learning activity event.
        </li>
        <li><strong>Correct it:</strong> edit your details on your profile page, or email us.</li>
        <li><strong>Delete it:</strong> your profile page → Delete account, or email us.</li>
        <li>
          <strong>Withdraw consent:</strong> turn Google Analytics off at any time from “Analytics choice” at the foot of
          every page; withdrawing is as easy as giving it. Deleting your account withdraws everything else.
        </li>
        <li><strong>Nominate someone</strong> to use these rights for you if you die or can no longer act: email us.</li>
        <li>
          <strong>Complain:</strong> write to our Grievance Officer (below). If you are not satisfied with the answer you
          may complain to the Data Protection Board of India.
        </li>
      </ul>
      <p>
        We answer within the times on the <Link href={LEGAL_DOCUMENTS.grievance.path}>Grievance Redressal</Link> page.
      </p>

      <h2>7. Cookies and your device</h2>
      <p>
        We use the cookies and device storage the service needs: the cookie that keeps you signed in, and your theme, your
        analytics choice and similar settings on your device. We don’t ask consent for those. Google Analytics sets its own
        cookies only after you allow it, and we delete them when you turn it off. There are no advertising cookies.
      </p>

      <h2>8. Security</h2>
      <p>
        Data is encrypted in transit and at rest. Access inside our team is limited to people who need it. No system is
        perfectly secure; if a breach affects your personal data we will tell you and the authorities as the law requires.
      </p>

      <h2>9. Changes</h2>
      <p>
        We update the version above when this policy changes and ask you to accept important changes before you continue
        using your account.
      </p>

      <h2>10. Contact</h2>
      <ContactList operatorLabel="Data fiduciary" />
      <p>
        See also the <Link href={LEGAL_DOCUMENTS.terms.path}>Terms of Service</Link>.
      </p>
    </>
  )
}
