prompt_origin="""
You will be provided with text from an image. Your task is to determine if it's a standard biographical entry and extract information if it is.

**Core Identification Rule (ALL conditions MUST be met sequentially):**

A text is a biographical entry **IF AND ONLY IF** it strictly follows the parsing and capitalization rules below.

**Step 1: Name Field Delimitation (The First Comma Rule)**

1.  The text **MUST** contain at least one comma. Find the position of the **very first comma**. If no comma exists, it is **NOT** a biographical entry. **Return `{}`.**
2.  **Isolate Potential Last Name:**
    *   `POTENTIAL_LASTNAME` is defined as all text from the start of the string up to (but not including) the first comma. Trim any whitespace.
    *   *Example:* For `STACE-SMITH, RICHARD, b. ...`, `POTENTIAL_LASTNAME` is exactly `STACE-SMITH`.
3.  **Isolate Potential First Name:**
    *   Let `REMAINDER_TEXT` be all text immediately *after* the first comma.
    *   *Example:* For `STACE-SMITH, RICHARD, b. ...`, `REMAINDER_TEXT` is ` RICHARD, b. ...`.
    *   Within `REMAINDER_TEXT`, find the start of the first biographical marker (e.g., `b.`, `m.`, `c.`) or a semicolon.
    *   `POTENTIAL_FIRSTNAME` is the text from the beginning of `REMAINDER_TEXT` up to that marker/semicolon.
    *   Finally, trim any leading/trailing whitespace and any trailing commas from `POTENTIAL_FIRSTNAME`.
    *   *Example:* The text in `REMAINDER_TEXT` before `b.` is ` RICHARD,`. After trimming, `POTENTIAL_FIRSTNAME` is `RICHARD`.
4.  **Validation:** If, after this process, `POTENTIAL_LASTNAME` or `POTENTIAL_FIRSTNAME` is empty, it is **NOT** a biographical entry. **Return `{}`.**

**Step 2: Last Name Capitalization Check**

1.  For each character in the `POTENTIAL_LASTNAME` identified in Step 1:
    *   If the character is a letter, it **MUST** be UPPERCASE.
    *   If it is not a letter, it **MUST** be a hyphen (`-`), apostrophe (`'`), space (` `), or parenthesis (`(` or `)`).
2.  If this rule is violated, it is **NOT** a biographical entry. **Return `{}` immediately.**

**Step 3: First Name (+ Suffix) Capitalization Check**

1.  For each character in the `POTENTIAL_FIRSTNAME` identified in Step 1:
    *   If the character is a letter, it **MUST** be UPPERCASE.
    *   If it is not a letter, it **MUST** be a period (`.`), hyphen (`-`), apostrophe (`'`), space (` `), or parenthesis (`(` or `)`).
2.  If this rule is violated, it is **NOT** a biographical entry. **Return `{}` immediately.**

**IF the text does NOT meet ALL of the above conditions, it is NOT a biographical entry. Return `{}`.**

Examples of **INVALID** starts (these will fail the Core Identification Rule and you MUST return `{}`):
*   `Can.`
*   `Smith, John David`
*   `SMITH, John`
*   `PFEIFFER`
*   `Pfeiffer vis. prof...`
*   `UPPERCASE,`

Examples of **VALID** starts:
*   `SMITH, JOHN DAVID`
*   `DOE, JANE R.`
*   `O'NEIL, PATRICK`
*   `LEE, CHUN-HEE`
*   `STACK-STAIKIDIS, WILLIAM JOHN`
*   `STACK (ALTERNATIVE), B(OGDAN) R., JR.`
*   `VAN DER POST, LAURENS` (Example with spaces in lastname)

**Information to Extract (ONLY IF the Core Identification Rule is fully met):**

*   `"lastname"`: The `POTENTIAL_LASTNAME` from Step 1.
*   `"firstname"`: The `POTENTIAL_FIRSTNAME` from Step 1.
    *   **Parentheses/Brackets Handling:** If parts of the name were originally enclosed in parentheses (e.g., "B(OGDAN)"), remove the parentheses themselves but retain the uppercase letters within them (e.g., becomes "BOGDAN"). For lastnames with parentheses like `STACK (ALTERNATIVE)`, the `lastname` field should include the content within parentheses as it was in `POTENTIAL_LASTNAME`, e.g., "STACK (ALTERNATIVE)".
*   `"b"`: The two-digit year from a `b. ... YY;` entry if present (e.g., `38` from `b. ... 38;`). If `b. YY;` is missing, use `null`.
*   `"m"`: The two-digit year from an `m. ... YY;` entry if present (e.g., `61` from `m. ... 61;`). If `m. YY;` is missing, use `null`.
*   `"c"`: The number from a `c. N;` entry if present (e.g., `3` from `c. 3;`). If `c. N;` is missing, use `null`.

**Content to IGNORE (these are contexts where you'd return `{}` because the Core Identification Rule would fail):**
*   Any text not strictly matching the parsing and capitalization format at the beginning.
*   Headers/Footers/Page Numbers (e.g., "4738 / PAFFENBARGER", "SMITH / 123").
*   Title Pages (e.g., "AMERICAN MEN AND WOMEN OF SCIENCE").
*   Copyright/Publisher Information, Prefaces, Tables of Content, Indexes.

Output MUST be ONLY the JSON object. Ensure string values are trimmed.
"""

prompt2="""
You will be provided with text from an image. Your task is to determine if it's a standard biographical entry and extract information if it is.

**Core Identification Rule (ALL conditions MUST be met sequentially):**

A text is a biographical entry **IF AND ONLY IF** it strictly follows the parsing and capitalization rules below.

**Step 1: Name Field Delimitation (The First Comma Rule)**

1.  The text **MUST** contain at least one comma. Find the position of the **very first comma**. This comma is the ONLY valid separator between the last name and the first name block. If no comma exists, it is **NOT** a biographical entry. **Return `{}`.**
2.  **Isolate Potential Last Name:**
    *   `POTENTIAL_LASTNAME` is defined as all text from the start of the string up to (but not including) the **very first comma**.
    *   **CRITICAL VALIDATION:** The resulting `POTENTIAL_LASTNAME` string **MUST NOT** contain any commas itself. If it does, the entry is malformed. **Return `{}` immediately.**
3.  **Isolate Potential First Name:**
    *   Let `REMAINDER_TEXT` be all text immediately *after* the **very first comma**.
    *   Within `REMAINDER_TEXT`, find the start of the first biographical marker (e.g., `b.`, `m.`, `c.`) or a semicolon that marks the end of the name.
    *   `POTENTIAL_FIRSTNAME` is the text from the beginning of `REMAINDER_TEXT` up to that marker/semicolon.
    *   Finally, trim any leading/trailing whitespace and any trailing commas from `POTENTIAL_FIRSTNAME`.
4.  **Validation:** If, after this process, `POTENTIAL_LASTNAME` or `POTENTIAL_FIRSTNAME` is empty, it is **NOT** a biographical entry. **Return `{}`.**

**Step 2: Capitalization Checks**

1.  **Last Name:** For each character in `POTENTIAL_LASTNAME`: if it's a letter, it **MUST** be UPPERCASE. If not a letter, it must be a hyphen (`-`), apostrophe (`'`), space (` `), or parenthesis (`(` or `)`).
2.  **First Name:** For each character in `POTENTIAL_FIRSTNAME`: if it's a letter, it **MUST** be UPPERCASE. If not a letter, it must be a period (`.`), hyphen (`-`), apostrophe (`'`), space (` `), or parenthesis (`(` or `)`).
3.  If any capitalization rule is violated, **Return `{}`.**

**IF the text does NOT meet ALL of the above conditions, it is NOT a biographical entry. Return `{}`.**

**Information to Extract (ONLY IF the Core Identification Rule is fully met):**

*   `"lastname"`: The `POTENTIAL_LASTNAME` from Step 1.
*   `"firstname"`: The `POTENTIAL_FIRSTNAME` from Step 1, exactly as it was identified. **Do not remove or alter the parentheses.** For example, `H(ANS) H(EINRICH)` should be extracted exactly as `H(ANS) H(EINRICH)`.
*   `"b"`: Scan the entire entry for the pattern `b. ... YY;` and extract the two-digit year `YY`. Ignore any other text (like `nat;`) that may appear nearby. If the pattern is not found, use `null`.
*   `"m"`: Scan the entire entry for the pattern `m. YY;` and extract the two-digit year `YY`. If there is more than one marry year, keep both (eg "m" : "00, 01"). If the pattern is not found, use `null`.
*   `"c"`: Scan the entire entry for the pattern `c. N;` and extract the number `N`. If the pattern is not found, use `null`.

**Content to IGNORE (these are contexts where you'd return `{}` because the Core Identification Rule would fail):**
*   Any text not strictly matching the parsing and capitalization format at the beginning.
*   Headers/Footers/Page Numbers (e.g., "4738 / PAFFENBARGER", "SMITH / 123").

Output MUST be ONLY the JSON object. Ensure string values are trimmed.
"""
prompt_scan_whole_page="""
```
You will be provided with text from an image. Your task is to determine if it's a standard biographical entry and extract information if it is.

**Core Identification Rule (ALL conditions MUST be met sequentially):**

A text is a biographical entry **IF AND ONLY IF** it strictly follows the parsing and capitalization rules below.

**Step 1: Name Field Delimitation (The First Comma Rule)**

1.  The text **MUST** contain at least one comma. Find the position of the **very first comma**. This comma is the ONLY valid separator between the last name and the first name block. If no comma exists, it is **NOT** a biographical entry. **Return `{}`.**
2.  **Isolate Potential Last Name:**
    *   `POTENTIAL_LASTNAME` is defined as all text from the start of the string up to (but not including) the **very first comma**.
    *   **CRITICAL VALIDATION:** The resulting `POTENTIAL_LASTNAME` string **MUST NOT** contain any commas itself. If it does, the entry is malformed. **Return `{}` immediately.**
3.  **Isolate Potential First Name:**
    *   Let `REMAINDER_TEXT` be all text immediately *after* the **very first comma**.
    *   Within `REMAINDER_TEXT`, find the start of the first biographical marker (e.g., `b.`, `m.`, `c.`) or a semicolon that marks the end of the name.
    *   `POTENTIAL_FIRSTNAME` is the text from the beginning of `REMAINDER_TEXT` up to that marker/semicolon.
    *   Finally, trim any leading/trailing whitespace and any trailing commas from `POTENTIAL_FIRSTNAME`.
4.  **Validation:** If, after this process, `POTENTIAL_LASTNAME` or `POTENTIAL_FIRSTNAME` is empty, it is **NOT** a biographical entry. **Return `{}`.**

**Step 2: Capitalization Checks**

1.  **Last Name:** For each character in `POTENTIAL_LASTNAME`: if it's a letter, it **MUST** be UPPERCASE. If not a letter, it must be a hyphen (`-`), apostrophe (`'`), space (` `), or parenthesis (`(` or `)`).
2.  **First Name:** For each character in `POTENTIAL_FIRSTNAME`: if it's a letter, it **MUST** be UPPERCASE. If not a letter, it must be a period (`.`), hyphen (`-`), apostrophe (`'`), space (` `), or parenthesis (`(` or `)`).
3.  If any capitalization rule is violated, **Return `{}`.**

**IF the text does NOT meet ALL of the above conditions, it is NOT a biographical entry. Return `{}`.**

**Information to Extract (ONLY IF the Core Identification Rule is fully met):**

*   `"lastname"`: The `POTENTIAL_LASTNAME` from Step 1.
*   `"firstname"`: The `POTENTIAL_FIRSTNAME` from Step 1, exactly as it was identified. **Do not remove or alter the parentheses.** For example, `H(ANS) H(EINRICH)` should be extracted exactly as `H(ANS) H(EINRICH)`.
*   `"b"`: Scan the entire entry for the pattern `b. (MM dd,) YY;` and extract the two-digit year `YY` (person's born year). If the pattern is not found, use `null`.
*   `"m"`: Scan the entire entry for the pattern `m. YY;` and extract the two-digit year `YY`. If there is more than one marry year, keep both (eg "m" : "00, 01"). If the pattern is not found, use `null`.
*   `"c"`: Scan the entire entry for the pattern `c. N;` and extract the number `N`. If the pattern is not found, use `null`.

**Content to IGNORE (these are contexts where you'd return `{}` because the Core Identification Rule would fail):**
*   Any text not strictly matching the parsing and capitalization format at the beginning.
*   Headers/Footers/Page Numbers (e.g., "4738 / PAFFENBARGER", "SMITH / 123").

Output MUST be ONLY the JSON object. Ensure string values are trimmed.
```
With the following prompt to determine an entry, please get apply it to the image, and producing me with following format
so like
[
{ "lastname": "EXAMPLE", "firstname": "EXAMPLE", "b" :"yy" , ... },
{ "lastname": "EXAMPLE", "firstname": "EXAMPLE", "b" :"yy" , ... },
{ "lastname": "EXAMPLE", "firstname": "EXAMPLE", "b" :"yy" , ... },
]

Output MUST be ONLY the JSON object/array. Ensure string values are trimmed. If not a biographical entry, return {}
"""

prompt3="""
Count the number of biographical entries. An entry is identified by a bolded or capitalized surname followed by a comma, first name(s), and then typical biographical data points such as "b. [birth date]", "m. [marriage date]", "c. [children count]".

Provide only the integer count. Do not include any text, punctuation, or spaces beyond the digit itself.
"""
prompt5="""
Count biographical entries.
To be counted, an entry MUST satisfy all of the following conditions:
1. It must start with a lastname part before the first comma. All ALPHABETIC characters in this lastname part MUST be UPPERCASE.
2. Immediately after the first comma, there must be a firstname part that begins with a capital letter.
3. This firstname part must be immediately followed by another comma.

This "Lastname, Firstname," structure is the key indicator of a person's entry, distinguishing it from subject headers which end in a period.
Both the lastname and firstname parts must be non-empty.
Ignore any text that is clearly a header or footer.

Your entire response MUST be a single integer representing the total count. Do not include any other words, explanations, lists, or reasoning. Output only the number itself.
"""
prompt_reconfirm="""
Text=secret

You will act as a strict data validator. Your goal is to determine if the first two elements of a list could form a person's name.

First, apply these disqualification rules to each of the first two strings ('SUMMERS' and 'spec lectr'):
- **Casing Rule:** If the string is entirely lowercase or has a majority of lowercase letters, it is DISQUALIFIED.
- **Content Rule:** If the string is a common non-name word, a job title, or an abbreviation (like 'spec lectr'), it is DISQUALIFIED.


Is Text[0] or Text[1] disqualified by any rule?
If EITHER of the first two strings is disqualified, the final answer is False.

Output only 'True' or 'False'.
"""
def fprompt_reconfirm(ask):
    return prompt_reconfirm.replace("secret", ask)
def prompt():
    result_prompt = prompt2
    #if(think):
    #    result_prompt = prompt_origin.replace("/no_think", "")
    return result_prompt

def prompt_asking_total_biographical():
    return prompt5