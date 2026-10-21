import Link from 'next/link'
import { ContactList } from './Fact'
import { LEGAL_DOCUMENTS } from './documents'

/**
 * Grievance Redressal: the Grievance Officer and the response times we commit to — IT (Intermediary Guidelines) Rules
 * 2021, rule 3(2), as amended on 10 February 2026 (G.S.R. 120(E)): acknowledge within 24 hours, resolve within 7 days,
 * act on removal requests within 36 hours.
 */
export function Grievance() {
  return (
    <>
      <p>
        If you have a complaint about LearnViaNotes — about your personal data, your account, or anything published on the
        site — write to our Grievance Officer.
      </p>

      <ContactList />

      <h2>How to complain</h2>
      <p>Email the Grievance Officer with:</p>
      <ul>
        <li>your name, and the email address of your LearnViaNotes account if you have one;</li>
        <li>what the complaint is about, with a link to the page, note, comment or profile, or a description of it;</li>
        <li>what you would like us to do.</li>
      </ul>
      <p>
        You don’t need to write to us to download your data or delete your account: both are on your profile page, under
        Your data. To report a note, comment, group or profile that breaks the rules, the Report button beside it is
        quickest; reports reach our moderators straight away.
      </p>

      <h2>How quickly we respond</h2>
      <ul>
        <li><strong>Acknowledgement:</strong> within 24 hours of receiving your complaint.</li>
        <li><strong>Resolution:</strong> within 7 days, with our reasons.</li>
        <li><strong>Content that breaks the law:</strong> if you ask us to remove it, we act within 36 hours.</li>
      </ul>
      <p>
        These are the times rule 3(2) of the Information Technology (Intermediary Guidelines and Digital Media Ethics Code)
        Rules, 2021 sets, as amended in February 2026; we apply them to every complaint.
      </p>

      <h2>If you’re not satisfied</h2>
      <p>
        Reply to our answer and the Grievance Officer will look at it again. For complaints about personal data you may also
        go to the Data Protection Board of India once you have used this process. Our{' '}
        <Link href={LEGAL_DOCUMENTS.privacy.path}>Privacy Policy</Link> explains your rights over your data.
      </p>
    </>
  )
}
