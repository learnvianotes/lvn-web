import Link from 'next/link'

/** The licence for content people share or make public — draft for the owner's review (§15.2, ADR-0010). */
export function Licence() {
  return (
    <>
      <p>
        You own what you write on LearnViaNotes. This licence covers only what we need to show your notes to the people you
        choose, and what others may do with notes you make public.
      </p>

      <h2>1. Private notes</h2>
      <p>Private notes are yours alone. We store and process them only to run the service for you.</p>

      <h2>2. What you allow us</h2>
      <p>
        For notes you share or make public, you give LearnViaNotes a worldwide, non-exclusive, royalty-free licence to
        store, copy, display and adapt them (for example to show them on phones, make previews and smaller pictures, or
        index them for search) — only to run and show LearnViaNotes. The licence ends when you make the note private or
        delete it, except for copies others already made (below) and backups that expire on their own.
      </p>

      <h2>3. Copies others make</h2>
      <ul>
        <li>
          People who can read your note may keep a copy in their own LearnViaNotes account, unless you turn off “Let people
          make a copy”.
        </li>
        <li>Every copy keeps a credit to you as the author, for good. Your note’s title is shown only to people who can still read it.</li>
        <li>A copy made of a shared (not public) note can never be made public.</li>
        <li>Copies already made stay with their makers if you later make your note private or turn copying off.</li>
      </ul>

      <h2>4. What you promise</h2>
      <p>
        You have the right to share what you upload. If you use someone else’s work, you have their permission, or the law
        allows it (for example short quotations with credit).
      </p>

      <h2>5. Reporting misuse</h2>
      <p>
        If you think a note uses your work without permission, report it as “Copied without permission”. Moderators will
        look at it and may remove the note. See the <Link href="/legal/terms">Terms of Service</Link>.
      </p>
    </>
  )
}
