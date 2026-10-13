import Link from 'next/link'

/** Privacy Policy — draft for the owner's review (§15.2, India's DPDP Act 2023). */
export function Privacy() {
  return (
    <>
      <p>
        This policy explains what [operator’s legal name] (“we”) collects when you use LearnViaNotes, why, and the choices
        you have. We do not sell your personal data and we do not show you advertising.
      </p>

      <h2>1. What we collect</h2>
      <ul>
        <li>Account: your name, email address, handle, date of birth, password (stored only as a secure hash) or your Google sign-in.</li>
        <li>Optional details: a college or organisation email to verify your account, your department and year of study.</li>
        <li>Your content: notes, the files you upload to them, folders, tags, shares and copies.</li>
        <li>Learning activity: what you study and revise, so that the app can plan your week.</li>
        <li>Technical data: sign-in sessions, the device you use, and error and security logs.</li>
      </ul>

      <h2>2. Why we use it</h2>
      <ul>
        <li>To run your account and show your notes to you and to the people you choose.</li>
        <li>To keep the community safe: moderation, preventing abuse, and protecting younger users.</li>
        <li>To fix problems and keep the service secure.</li>
        <li>To send you emails you need (confirming your address, security notices) and the ones you asked for.</li>
      </ul>
      <p>We process your data with your consent and, where the law allows, for these legitimate uses.</p>

      <h2>3. Who else sees it</h2>
      <ul>
        <li>The people you share notes with, and anyone, for notes you make public.</li>
        <li>
          Service providers that run parts of LearnViaNotes for us, under contract: hosting and storage (Amazon Web
          Services, in India), email delivery, Google for Google sign-in, and error reporting.
        </li>
        <li>
          AI features, when they arrive, send only the text needed for the task to the AI provider — never your name or
          account details.
        </li>
        <li>Authorities, when the law requires it.</li>
      </ul>

      <h2>4. Younger users</h2>
      <p>
        We ask for your date of birth. Accounts of people under 18 stay limited (private notes and classes only) until a
        parent, guardian or school confirms consent, and we do not use their activity for behavioural recommendations.
      </p>

      <h2>5. How long we keep it</h2>
      <ul>
        <li>Your notes and files: until you delete them (deleted notes stay in the trash for 30 days).</li>
        <li>Learning activity: 24 months, then only as totals.</li>
        <li>Security and moderation records: up to 7 years. Technical logs: 30 days.</li>
        <li>When you delete your account, we delete your personal data and files, except what the law requires us to keep.</li>
      </ul>

      <h2>6. Your rights</h2>
      <ul>
        <li>See and download your data (account page → Export).</li>
        <li>Correct your details, and delete your account.</li>
        <li>Withdraw consent — some features may then stop working.</li>
        <li>Complain to our grievance officer, and then to the Data Protection Board of India.</li>
      </ul>

      <h2>7. Cookies</h2>
      <p>
        We use only the cookies the service needs, such as the one that keeps you signed in. There are no third-party
        trackers or advertising cookies.
      </p>

      <h2>8. Security</h2>
      <p>
        Data is encrypted in transit and at rest. Access inside our team is limited to people who need it. If a breach
        affects you, we tell you and the authorities as the law requires.
      </p>

      <h2>9. Changes and contact</h2>
      <p>
        We update the version above when this policy changes and ask you to accept important changes. Grievance officer:
        [name], [grievance email]. See also the <Link href="/legal/terms">Terms of Service</Link>.
      </p>
    </>
  )
}
