# General Style Guide

In general, all messages should be kept lowercase - with the exception of slash command autocompletes, and embeds, where both the embed's main and sub title should be written using [AP Stylebook Title Case](https://en.wikipedia.org/wiki/Title_case#AP_Stylebook), if this is either uncommon or doesn't apply to your language, don't do it - but do mention what style you've used in your pull request so it can be documented for future contributions.

Companies are entities, and should follow the casing of your country's language

The bot speaks in first person

If translating to a language where the speaker's gender matters, the bot is gender non-conforming, if not possible, it's feminine


# how to write

## before you start
Use VS Code or another code editor is recommended so that you don't accidentally malform the translation data

If using VS code, change json5 files to "json5" or "json with comments", this can be done by pressing the button labeled "JSON" in the bottom right corner, and searching for "JSON5" (it allows for comments and trailing commas)

## howto
When adding a translation, simply copy over the key from the en-GB.json5 file, and write in your translation as the value

NEVER touch the translation keys, even if they have typos in them - they won't be shown to the user anyways so it's more bother than it's worth

The above also applies to the variables found within the curly brackets {}

Links shall not specify their protocol (i.e https://), so www.xyz is good, https://www.xyz is bad

## uploading your changes
I can't give exact details on how to contribute, but in short just create a merge/pull request - if you need help, contact me

# technical info
If a translation value for a given key isn't found, or a command fails to fetch a user's locale, it will default to the key found in en-GB as it'll be the most up-to-date one (i REFUSE to write color)

As for the time being, the bot's status message is not being translated, though this may be added in the future if it's possible thru sharding