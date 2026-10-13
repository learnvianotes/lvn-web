import Link from 'next/link'

/** Terms of Service — draft for the owner's review (§15.2). */
export function Terms() {
  return (
    <>
      <p>
        LearnViaNotes is a place to write notes, study with them and share them. These terms are the agreement between you
        and [operator’s legal name] (“we”) when you use the website, the apps and the API. Please read them with the{' '}
        <Link href="/legal/privacy">Privacy Policy</Link> and the <Link href="/legal/content-licence">Content licence</Link>.
      </p>

      <h2>1. Who can use LearnViaNotes</h2>
      <ul>
        <li>You give your real date of birth when you sign up. We use it to keep younger people safe, never to show to others.</li>
        <li>
          If you are under 18 (or the age of digital consent where you live), your account is limited until a parent,
          guardian or your school confirms consent: you can write private notes and take part in your classes, but you
          cannot make notes public or receive direct messages.
        </li>
        <li>One person, one account. Keep your password safe and tell us if someone else gets into your account.</li>
      </ul>

      <h2>2. Your notes</h2>
      <ul>
        <li>Your notes are yours. Private notes are visible only to you.</li>
        <li>
          When you share a note or make it public, you give us the licence described in the{' '}
          <Link href="/legal/content-licence">Content licence</Link>, so that we can show it to the people you chose.
        </li>
        <li>You only upload things you have the right to share.</li>
      </ul>

      <h2>3. Community rules</h2>
      <p>Do not use LearnViaNotes to:</p>
      <ul>
        <li>bully, harass, threaten or shame anyone;</li>
        <li>attack people for who they are (hate), or share sexual content;</li>
        <li>encourage self-harm — if you are struggling, please talk to someone you trust or a local helpline;</li>
        <li>post spam or advertising, or try to get around limits, security or moderation;</li>
        <li>share other people’s work without permission, or their personal information.</li>
      </ul>

      <h2>4. Moderation</h2>
      <ul>
        <li>
          Notes going public are checked automatically first; some wait for a moderator. Anyone can report content that
          breaks these rules.
        </li>
        <li>
          Moderators may hide or remove content and warn or limit accounts. We tell you what happened and why, and you can
          appeal a hidden or removed note once.
        </li>
        <li>
          Copyright owners can report work used without permission (“Copied without permission” when reporting). People
          who repeatedly infringe lose their account.
        </li>
      </ul>

      <h2>5. Ending your account</h2>
      <p>
        You can export your data and delete your account at any time from your account page. We may suspend or close
        accounts that seriously or repeatedly break these terms; where we can, we tell you first and let you export your
        notes.
      </p>

      <h2>6. The service</h2>
      <p>
        We work hard to keep LearnViaNotes available and your notes safe, but the service is provided “as is”. Study notes
        written by other people may contain mistakes — check what matters. To the extent the law allows, we are not liable
        for indirect losses, and our total liability is limited to [amount].
      </p>

      <h2>7. Changes</h2>
      <p>
        When we change these terms in a way that matters, we update the version above and ask you to accept the new terms
        before you continue using your account.
      </p>

      <h2>8. Law and contact</h2>
      <p>
        These terms are governed by the laws of India; courts in [city] have jurisdiction. Questions:{' '}
        [contact email].
      </p>
    </>
  )
}
