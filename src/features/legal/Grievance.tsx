/* Grievance Redressal — the Grievance Officer and the response times we commit to. */

import { Link } from 'react-router-dom'
import { APP_NAME } from '@/config'
import { Fact, Mailbox } from './Fact'

export function Grievance() {
  return (
    <>
      <p className="lead">
        If you have a complaint about {APP_NAME} — about your personal data, your account, or any content on the site —
        write to our Grievance Officer.
      </p>

      <dl className="legal-contact">
        <dt>Grievance Officer</dt><dd><Fact field="grievanceOfficer" /></dd>
        <dt>Email</dt><dd><Mailbox /></dd>
        <dt>Post</dt><dd><Fact field="address" /></dd>
        <dt>On behalf of</dt><dd><Fact field="operator" />, which runs {APP_NAME}</dd>
      </dl>

      <h2>How to complain</h2>
      <p>Email the Grievance Officer with:</p>
      <ul>
        <li>your name, and the email address of your {APP_NAME} account if you have one;</li>
        <li>what the complaint is about, with a link to the page or a description of the content;</li>
        <li>what you would like us to do.</li>
      </ul>
      <p>
        To delete your account or download your data you don’t need to write to us: both are in Settings → Your data.
        For mistakes in the notes, the Help center’s Report form is quickest.
      </p>

      <h2>How quickly we respond</h2>
      <ul>
        <li><strong>Acknowledgement:</strong> within 24 hours of receiving your complaint.</li>
        <li><strong>Resolution:</strong> within 7 days, with our reasons.</li>
        <li><strong>Content that breaks the law:</strong> if you ask us to remove it, we act within 36 hours.</li>
      </ul>
      <p>
        These are the times rule 3(2) of the Information Technology (Intermediary Guidelines and Digital Media Ethics
        Code) Rules, 2021 sets, as amended in February 2026; we apply them to every complaint.
      </p>

      <h2>If you’re not satisfied</h2>
      <p>
        Reply to our answer and the Grievance Officer will look at it again. For complaints about personal data you may
        also go to the Data Protection Board of India once you have used this process. Our{' '}
        <Link to="/privacy">Privacy Policy</Link> explains your rights over your data.
      </p>
    </>
  )
}
