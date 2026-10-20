/* The Terms of Use. */

import { Link } from 'react-router-dom'
import { APP_NAME } from '@/config'
import { Fact, Mailbox } from './Fact'

export function Terms() {
  return (
    <>
      <p className="lead">
        These terms are an agreement between you and <Fact field="operator" />, who runs {APP_NAME} (“we”, “us”). By
        using {APP_NAME} you accept them. Please also read the <Link to="/privacy">Privacy Policy</Link>, which explains
        how we handle your personal data.
      </p>

      <h2>1. Who can use {APP_NAME}</h2>
      <p>
        Anyone may read the notes without an account. Accounts are only for people who are 18 or older: by creating
        one you confirm that you are. We delete accounts that belong to someone under 18.
      </p>

      <h2>2. The service</h2>
      <p>
        {APP_NAME} offers study notes, coding problems with solutions and study tools for computer-science interview
        preparation. It is free to use. We may add, change or stop features; when a change affects your account or
        your data, we will tell you in the app first.
      </p>

      <h2>3. Your account</h2>
      <ul>
        <li>Give your real email address and keep your password to yourself. An account is for one person.</li>
        <li>You are responsible for what happens under your account. Tell us at once if you think someone else has used it.</li>
        <li>You can delete your account at any time from Settings → Your data.</li>
      </ul>

      <h2>4. Fair use</h2>
      <p>Please don’t:</p>
      <ul>
        <li>copy the notes or problems in bulk, scrape the site, or republish, sell or rent its content;</li>
        <li>try to break into, overload or disrupt the service, or get at anyone else’s data;</li>
        <li>send spam, abuse or unlawful material through the feedback form;</li>
        <li>use {APP_NAME} in any way that breaks the law.</li>
      </ul>
      <p>We may suspend or close an account that breaks these rules. Where it is fair to, we will tell you why first.</p>

      <h2>5. Our content</h2>
      <p>
        The notes, problems, solutions, code and design of {APP_NAME} belong to us or to those who licensed them to us.
        You may read, print and copy them for your own personal study, and use the code samples in your own learning
        projects. Anything more — republishing, teaching material for sale, or other commercial use — needs our written
        permission. Problem numbers and names of other platforms belong to their owners and are used only to identify
        the problems.
      </p>

      <h2>6. Your notes and feedback</h2>
      <p>
        Your personal notes stay yours and private to your account; we store them only to provide the service. If you
        send us feedback or suggestions, you allow us to use them to improve {APP_NAME} without paying you.
      </p>

      <h2>7. Accuracy</h2>
      <p>
        We check our content carefully, but notes and code can still contain mistakes and can go out of date. The
        content is for learning; it is not professional advice, and we can’t promise any interview or exam result. If
        you find a mistake, please report it from the Help center.
      </p>

      <h2>8. Our responsibility</h2>
      <p>
        {APP_NAME} is provided free and “as is”. As far as the law allows, we are not liable for indirect or
        consequential loss, or for lost data or opportunities, arising from your use of the service. Nothing in these
        terms limits any right you have that the law does not allow us to limit.
      </p>

      <h2>9. Ending</h2>
      <p>
        You may stop using {APP_NAME} and delete your account at any time. If we ever close the service, we will give
        signed-in users notice in the app and time to download their data.
      </p>

      <h2>10. Law and disputes</h2>
      <p>
        These terms are governed by the laws of India. Please write to us first so we can try to sort out any problem.
        Otherwise, the courts at <Fact field="courtsCity" /> have jurisdiction.
      </p>

      <h2>11. Complaints and contact</h2>
      <p>
        Complaints, including about content on {APP_NAME}, go to our Grievance Officer, <Fact field="grievanceOfficer" />,
        at <Mailbox />. The <Link to="/grievance">Grievance Redressal</Link> page says how and how quickly we respond.
      </p>

      <h2>12. Changes to these terms</h2>
      <p>
        When we change these terms we update the date at the top. For changes that matter, we will tell signed-in users
        in the app before they apply. If you keep using {APP_NAME} after that, the new terms apply.
      </p>
    </>
  )
}
