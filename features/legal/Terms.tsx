import Link from 'next/link'
import { ACCOUNTS_FROM_AGE, RETENTION } from '@/config/legal'
import { Fact, Mailbox } from './Fact'
import { LEGAL_DOCUMENTS } from './documents'

/** Terms of Service — draft for the owner's review (§15.2). The operator's details come from config/legal.ts. */
export function Terms() {
  return (
    <>
      <p>
        LearnViaNotes is a place to write notes, study with them and share them. These terms are the agreement between you
        and <Fact field="operator" /> (“we”) when you use the website, the apps and the API. Please read them with the{' '}
        <Link href="/legal/privacy">Privacy Policy</Link> and the <Link href="/legal/content-licence">Content licence</Link>.
      </p>

      <h2>1. Who can use LearnViaNotes</h2>
      <ul>
        <li>Anyone may read public notes and subjects without an account.</li>
        <li>
          Accounts are only for people who are {ACCOUNTS_FROM_AGE} or older. You give your real date of birth when you
          sign up, and by creating an account you confirm you are {ACCOUNTS_FROM_AGE} or older. We delete accounts that
          belong to someone younger.
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
        You can download your data and delete your account at any time from your profile page; the account goes{' '}
        {RETENTION.deletionGraceDays} days after you ask, and you can change your mind until then. We don’t delete an
        account nobody asked us to delete, unless it belongs to someone under {ACCOUNTS_FROM_AGE} or seriously or
        repeatedly breaks these terms: then we may suspend or close it, and where we can, we tell you first and let you
        download your data.
      </p>

      <h2>6. The service</h2>
      <p>
        We work hard to keep LearnViaNotes available and your notes safe, but the service is provided “as is”. Study notes
        written by other people may contain mistakes — check what matters. As far as the law allows, we are not liable for
        indirect or consequential loss, or for lost data or opportunities, arising from your use of the service. Nothing in
        these terms limits any right you have that the law does not allow us to limit.
      </p>

      <h2>7. Changes</h2>
      <p>
        When we change these terms in a way that matters, we update the version above and ask you to accept the new terms
        before you continue using your account.
      </p>

      <h2>8. Law and disputes</h2>
      <p>
        These terms are governed by the laws of India. Please write to us first so we can try to sort out any problem;
        otherwise, the courts at <Fact field="courtsCity" /> have jurisdiction.
      </p>

      <h2>9. Complaints and contact</h2>
      <p>
        Complaints, including about anything published on LearnViaNotes, go to our Grievance Officer,{' '}
        <Fact field="grievanceOfficer" />, at <Mailbox />. The{' '}
        <Link href={LEGAL_DOCUMENTS.grievance.path}>Grievance Redressal</Link> page says how, and how quickly we respond:
        within 24 hours to acknowledge, 7 days to resolve, and 36 hours to act on a request to remove unlawful content.
      </p>
    </>
  )
}
