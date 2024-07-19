# general style guide

in general, all messages should be kept lowercase - with the exception of embeds, where the main and sub titles should be written in [AP Stylebook Title Case](https://en.wikipedia.org/wiki/Title_case#AP_Stylebook) if this is either uncommon or doesn't apply to your language, don't do it - but do mention what style you've used in your pull request so it can be added to the list.

the bot speaks in first person, it should never refer to itself as "the bot"

if translating to a language where the speaker's gender matters, the bot is gender non-conforming, if not possible, it's feminine


# how to write

## before you start

vscode or another code editor is recommended so that you don't accidentally malform it

if using vscode, change json5 files to "json5" or "json with comments", this can be done by pressing the button labeled "JSON" in the bottom right corner, and searching for "JSON5" (it allows for comments and trailing commas)

## howto

when adding a translation, simply copy over the key from the en-GB.json5 file, and write in your translation as the value

NEVER touch the translation keys, even if they have typos in them - they won't be shown to the user anyways so it's more bother than it's worth

the above also applies to the variables found within the curly brackets {}


# technical info

if a translation value for a given key isn't found, or a command fails to fetch a user's locale, it will default to the key found in en-GB as it'll be the most up-to-date one (i REFUSE to write color)

as for the time being, the bot's status message is not being translated, though this may be added in the future if it's possible thru sharding