/**
 * A title for a page under the site's "%s · LearnViaNotes" template. Next fills the template with String.replace
 * (`template.replace(/%s/g, title)`), so a "$&", "$'" or "$1" in a note's, a person's or a resource's title would be
 * read as a replacement pattern and garble the page's title. Doubling each "$" keeps it a "$".
 * Only for templated titles: `{ absolute }` titles and Open Graph titles are used as they are.
 */
export const templated = (title: string): string => title.replace(/\$/g, '$$$$')
