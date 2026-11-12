import Link from 'next/link'
import { RETENTION } from '@/config/legal'
import { Mailbox } from './Fact'

/**
 * Public account-deletion page (no sign-in). Google Play’s data-deletion URL points here.
 * Steps and names are the ones in the app: Your account, Delete your account, My Notes, Trash,
 * Move to trash, Delete card, Remove picture. Times are RETENTION and requestAccountDeletion
 * (lvn-backend ADR-0088): 14 days, private notes and learning history go, public notes, posts
 * and comments stay as “Deleted user”.
 */
export function AccountDeletionPage() {
  return (
    <div className="mx-auto flex w-full max-w-3xl flex-col gap-8 px-4 py-10">
      <header className="flex flex-col gap-2">
        <h1 className="text-3xl font-extrabold tracking-tight">Delete your account</h1>
        <p className="leading-relaxed text-muted">
          You can read this page without an account. The website and the app use the same screens. Deleting the
          account is done while you are signed in, or by email from the address on the account.
        </p>
      </header>

      <section className="flex flex-col gap-3" aria-labelledby="delete-in-app">
        <h2 id="delete-in-app" className="text-xl font-bold">
          On the website and in the app
        </h2>
        <ol className="flex list-decimal flex-col gap-2 pl-5 leading-relaxed">
          <li>
            <Link href="/sign-in" className="text-accent">
              Sign in
            </Link>
            .
          </li>
          <li>
            Open <strong>Your account</strong>. It is the round button in the top bar, on a computer and on a phone.
          </li>
          <li>
            On that page, find the section <strong>Delete your account</strong>.
          </li>
          <li>
            If the account has a password, enter it under <strong>Your password</strong>. If you sign in with Google,
            leave <strong>Your password</strong> empty.
          </li>
          <li>
            Type <strong>DELETE</strong> in <strong>Type DELETE to confirm</strong>.
          </li>
          <li>
            Choose <strong>Delete my account</strong>.
          </li>
        </ol>
        <p className="leading-relaxed">
          The account is deleted {RETENTION.deletionGraceDays} days later. Until that day, every signed-in page says
          “Your account will be deleted on” that date, and <strong>Keep my account</strong> cancels the deletion.
          Asking also signs every other device out.
        </p>
      </section>

      <section className="flex flex-col gap-3" aria-labelledby="delete-by-email">
        <h2 id="delete-by-email" className="text-xl font-bold">
          By email
        </h2>
        <p className="leading-relaxed">
          Write to <Mailbox /> from the email address on the account. In the message, say that you want the account
          deleted, and include the handle shown under your name on <strong>Your account</strong> (it looks like
          @name).
        </p>
        <p className="leading-relaxed">
          That request follows the same rules as <strong>Delete my account</strong>: the account goes{' '}
          {RETENTION.deletionGraceDays} days after we can match it. Email again from the same address before that day
          if you want to keep it.
        </p>
      </section>

      <section className="flex flex-col gap-3" aria-labelledby="what-is-deleted">
        <h2 id="what-is-deleted" className="text-xl font-bold">
          What is deleted, and what is kept
        </h2>
        <p className="leading-relaxed">After the {RETENTION.deletionGraceDays} days, we delete:</p>
        <ul className="flex list-disc flex-col gap-1 pl-5 leading-relaxed">
          <li>the account;</li>
          <li>your private notes and the files in them;</li>
          <li>your learning history.</li>
        </ul>
        <p className="leading-relaxed">We keep:</p>
        <ul className="flex list-disc flex-col gap-1 pl-5 leading-relaxed">
          <li>notes you made public, and your posts and comments, shown as by “Deleted user”;</li>
          <li>copies in backups, which are overwritten within {RETENTION.backupDays} days;</li>
          <li>server logs for {RETENTION.logsDays} days, and security and moderation records for up to {RETENTION.auditYears} years;</li>
          <li>a record for longer when the law requires it, for example to deal with a legal claim.</li>
        </ul>
      </section>

      <section className="flex flex-col gap-3" aria-labelledby="delete-part">
        <h2 id="delete-part" className="text-xl font-bold">
          Delete a note or an upload, and keep the account
        </h2>
        <h3 className="text-base font-bold">A note</h3>
        <ol className="flex list-decimal flex-col gap-2 pl-5 leading-relaxed">
          <li>
            Open the note from <strong>My Notes</strong>.
          </li>
          <li>
            On a phone, open <strong>More</strong> and choose <strong>Move to trash</strong>. On a wider screen, choose{' '}
            <strong>Move to trash</strong> on the note.
          </li>
          <li>Confirm “Move this note to the trash? You can restore it for 30 days.”</li>
        </ol>
        <p className="leading-relaxed">
          The note stays under <strong>My Notes</strong> → <strong>Trash</strong> for {RETENTION.trashDays} days.{' '}
          <strong>Restore</strong> puts it back. <strong>Delete forever</strong> removes it immediately, after you
          confirm “Delete this note for good? This cannot be undone.” After {RETENTION.trashDays} days a note still in
          the trash is deleted for good, including the files in it.
        </p>
        <h3 className="text-base font-bold">An upload</h3>
        <ul className="flex list-disc flex-col gap-2 pl-5 leading-relaxed">
          <li>
            A picture, video, recording or file that is a card in a note: open <strong>Card options</strong> on that
            card and choose <strong>Delete card</strong>. That removes the card from the note.
          </li>
          <li>
            A picture placed on a page: select it and choose <strong>Remove picture</strong>.
          </li>
        </ul>
        <p className="leading-relaxed">
          A file that only lives in a note leaves with that note. It stays in the trash with the note for{' '}
          {RETENTION.trashDays} days, unless you choose <strong>Delete forever</strong>.
        </p>
      </section>

      <p className="leading-relaxed">
        The same rules are in the <Link href="/legal/privacy" className="text-accent">Privacy Policy</Link>.
      </p>
    </div>
  )
}
