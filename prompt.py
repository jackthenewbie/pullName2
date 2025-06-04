prompt_origin="""
You will be provided with an image. Your task is to analyze the text content within this image.
Determine if the text in the image represents a standard biographical entry, as opposed to other text elements like headers or index lines.

**Key Features of a Biographical Entry (ALL these primary features should be present for a positive ID):**
1.  The entry **must** begin with a person's name in the format: `LASTNAME, FIRSTNAME [MIDDLE_INFO]`. All parts of the name are typically capitalized. A lone lastname, or a lastname preceded only by a number/symbol, is NOT a biographical entry.
2.  This full name structure **must** be followed very closely (often immediately) by `b.` (indicating "born"), then details including a two-digit birth year (e.g., `b. City, State, Mon. DD, YY;`).
3.  The combination of `LASTNAME, FIRSTNAME ... b. ... YY;` is the definitive sequence. Without the `b.` details immediately following a full name, it is NOT a biographical entry.

**Secondary Features (often present but not definitive without the primary ones):**
*   May also contain `m. YY;` (married year) and `c. N;` (number of children) after the birth information.
*   The entry is usually a dense block of text with many abbreviations and uses semicolons to separate distinct pieces of information (degrees, jobs).

**Content to IGNORE (if the image's text primarily shows these, or if primary biographical features are missing, return {}):**
*   **Headers/Footers/Page Numbers:** Text that is clearly a page identifier, often a number followed by a single name or word (e.g., "4738 / PAFFENBARGER", "SMITH / 123"). These lack the `FIRSTNAME` and the crucial `b. ... YY;` details.
*   **Title Pages:** Large, centered text (e.g., "AMERICAN MEN AND WOMEN OF SCIENCE").
*   **Copyright/Publisher Information:** Text like "Copyright ©", "Published by", "ISBN:".
*   **Lists of Personnel/Contributors not following the full biographical pattern:** e.g., "Dr. Mina Rees, President...", "Chairman: Dr. John G. Truxal...". These lack the specific `LASTNAME, FIRSTNAME ... b. ... YY;` sequence.
*   **Other non-biographical content:** Prefaces, tables of content, indexes.
*   **Any text block that does not start with `LASTNAME, FIRSTNAME` followed by `b. ... YY;`**.

**Your Instructions:**

Analyze the text derived from the input image:

IF the text from the image does NOT meet ALL the primary "Key Features of a Biographical Entry" described above (especially the `LASTNAME, FIRSTNAME ... b. ... YY;` sequence):
    Return an empty JSON object:
    `{}`

ELSE (if the text from the image IS clearly identified as a biographical entry by meeting all primary features):
    Extract the following information from the biographical entry text into a JSON object:
    *   `"lastname"`: The person's last name, as it appears (must be all uppercase).
    *   `"firstname"`: The person's first name(s) and any middle name or initial, as it appears (must be all uppercase).
    *   `"b"`: The two-digit year from the `b.` entry (e.g., `38` from `b. ... 38;`). If missing, use `null`.
    *   `"m"`: The two-digit year from the `m.` entry (e.g., `61` from `m. 61;`). If missing, use `null`.
    *   `"c"`: The number from the `c.` entry (e.g., `3` from `c. 3.`). If missing, use `null`.

Output MUST be ONLY the JSON object. Ensure string values are trimmed.
"""

prompt2="""
You will be provided with an image. Your task is to analyze the text content within this image.
Determine if the text in the image represents a standard biographical entry, as opposed to other text elements like headers or index lines.

**Key Features of a Biographical Entry (ALL these primary features should be present for a positive ID):**
1.  The entry **must** begin with a person's name (they must be all in capitalized, if not return {} now) in the format: `LASTNAME, FIRSTNAME [MIDDLE_INFO]`. All parts of the name are capitalized. A lone lastname, or a lastname preceded only by a number/symbol, is NOT a biographical entry.
2.  This full name structure **must** be followed very closely (often immediately) by `b.` (indicating "born"), then details including a two-digit birth year (e.g., `b. City, State, Mon. DD, YY;`).
3.  The combination of `LASTNAME, FIRSTNAME ... b. ... YY;` is the definitive sequence. Without the `b.` details immediately following a full name, it is NOT a biographical entry.

**Secondary Features (often present but not definitive without the primary ones):**
*   May also contain `m. YY;` (married year) and `c. N;` (number of children) after the birth information.
*   The entry is usually a dense block of text with many abbreviations and uses semicolons to separate distinct pieces of information (degrees, jobs).

**Content to IGNORE (if the image's text primarily shows these, or if primary biographical features are missing, return {}):**
*   **Headers/Footers/Page Numbers:** Text that is clearly a page identifier, often a number followed by a single name or word (e.g., "4738 / PAFFENBARGER", "SMITH / 123"). These lack the `FIRSTNAME` and the crucial `b. ... YY;` details.
*   **Title Pages:** Large, centered text (e.g., "AMERICAN MEN AND WOMEN OF SCIENCE").
*   **Copyright/Publisher Information:** Text like "Copyright ©", "Published by", "ISBN:".
*   **Lists of Personnel/Contributors not following the full biographical pattern:** e.g., "Dr. Mina Rees, President...", "Chairman: Dr. John G. Truxal...". These lack the specific `LASTNAME, FIRSTNAME ... b. ... YY;` sequence.
*   **Other non-biographical content:** Prefaces, tables of content, indexes.
*   **Any text block that does not start with `LASTNAME, FIRSTNAME` followed by `b. ... YY;`**.
*   **Any text block that doesn't have LASTNAME, FIRSTNAME  capitalized (both must be capitalized, all letter in name)
*
**Your Instructions:**

Analyze the text derived from the input image:

IF the text from the image does NOT meet ALL the primary "Key Features of a Biographical Entry" described above (especially the `LASTNAME, FIRSTNAME ... b. ... YY;` sequence):
    Return an empty JSON object:
    `{}`

ELSE (if the text from the image IS clearly identified as a biographical entry by meeting all primary features):
    Extract the following information from the biographical entry text into a JSON object:
    *   `"lastname"`: The person's last name, as it appears (typically all uppercase).
    *   `"firstname"`: The person's first name(s) and any middle name or initial, as it appears (typically all uppercase). **Crucially, if parts of the first or middle name are enclosed in parentheses or brackets, remove the parentheses/brackets themselves but retain the letters within them, integrating them into the name.** For example, if the name appears as "J(OHN) D(OE)", it MUST be extracted as "JOHN DOE". Maintain capitalization.
    *   `"b"`: The two-digit year from the `b.` entry (e.g., `38` from `b. ... 38;`). If missing, use `null` (null for json, not a string).
    *   `"m"`: The two-digit year from the `m.` entry (e.g., `61` from `m. 61;`). If missing, use `null` (null for json, not a string).
    *   `"c"`: The number from the `c.` entry (e.g., `3` from `c. 3.`). If missing, use `null` (null for json, not a string).

Output MUST be ONLY the JSON object. Ensure string values are trimmed.
"""
prompt2_5="""
You will be provided with an image. Your task is to analyze the text content within this image.
Determine if the text in the image represents a standard biographical entry.

**Core Identification Rule (MUST BE MET):**

1.  **Strict Name Format and Capitalization at the Beginning:**
    *   The entry **must** begin with a person's name.
    *   This name **must** strictly adhere to the format: `LASTNAME, FIRSTNAME`.
        *   The `LASTNAME` is the text before the first comma.
        *   The `FIRSTNAME` is the text immediately following the first comma.
        *   Optional middle names or initials (`[MIDDLE_INFO]`) can follow the `FIRSTNAME`.
    *   **CRUCIAL "MUST MUST MUST MUST" ENFORCED RULE:** Both the `LASTNAME` part AND the `FIRSTNAME` part **MUST consist entirely of UPPERCASE letters.**
        *   Example of a valid start: `SMITH, JOHN DAVID` or `DOE, JANE R.`
        *   Examples of INVALID starts (these are NOT biographical entries and you MUST return {}):
            *   `Smith, John David` (Lastname not fully uppercase)
            *   `SMITH, John` (Firstname not fully uppercase)
            *   `Pfeiffer vis. prof...` (Neither "Pfeiffer" is fully uppercase, nor is it followed by a comma and an uppercase firstname. This is NOT a biographical entry.)
            *   `DOE` (Lone lastname, missing `, UPPERCASE_FIRSTNAME` structure)
            *   `PFEIFFER` (Lone uppercase lastname, but missing `, UPPERCASE_FIRSTNAME` structure)
    *   If the text does not start with this exact `UPPERCASE_LASTNAME, UPPERCASE_FIRSTNAME` structure (both parts fully capitalized and separated by a comma), it is **NOT** a biographical entry. **Return `{}` immediately in this case.**

**Information to Extract (if the Core Identification Rule is met):**
Once an entry is identified as biographical based SOLELY on the `UPPERCASE_LASTNAME, UPPERCASE_FIRSTNAME` rule:
*   Look for birth year (`b. YY;`), marriage year (`m. YY;`), and number of children (`c. N;`). These are **not** required for identification but should be extracted if present.

**Content to IGNORE (if the image's text primarily shows these, or if the Core Identification Rule above is NOT met, return {}):**
*   Any text not starting with the `UPPERCASE_LASTNAME, UPPERCASE_FIRSTNAME` structure (e.g., "Pfeiffer vis. prof...").
*   Headers/Footers/Page Numbers: Text that is clearly a page identifier (e.g., "4738 / PAFFENBARGER", "SMITH / 123").
*   Title Pages: Large, centered text (e.g., "AMERICAN MEN AND WOMEN OF SCIENCE").
*   Copyright/Publisher Information: Text like "Copyright ©", "Published by", "ISBN:".
*   Lists of Personnel/Contributors not following the `UPPERCASE_LASTNAME, UPPERCASE_FIRSTNAME` pattern.
*   Other non-biographical content: Prefaces, tables of content, indexes.

**Your Instructions:**

Analyze the text derived from the input image:

IF the text from the image does NOT strictly meet the **Core Identification Rule** (`UPPERCASE_LASTNAME, UPPERCASE_FIRSTNAME` at the very beginning):
    Return an empty JSON object:
    `{}`

ELSE (if the text IS identified as a biographical entry based SOLELY on the `UPPERCASE_LASTNAME, UPPERCASE_FIRSTNAME` rule):
    Extract the following information into a JSON object:
    *   `"lastname"`: The person's last name (the `UPPERCASE_LASTNAME` part before the first comma).
    *   `"firstname"`: The person's first name(s) and any middle name or initial (the `UPPERCASE_FIRSTNAME [MIDDLE_INFO]` part starting immediately after the first comma). **Crucially, if parts of the first or middle name are enclosed in parentheses or brackets, remove the parentheses/brackets themselves but retain the letters within them, integrating them into the name.** For example, if the name appears as "J(OHN) D(OE)", it MUST be extracted as "JOHN DOE". Maintain capitalization.
    *   `"b"`: The two-digit year from a `b. ... YY;` entry if present (e.g., `38` from `b. ... 38;`). If `b. YY;` is missing, use `null`.
    *   `"m"`: The two-digit year from an `m. ... YY;` entry if present (e.g., `61` from `m. ... 61;`). If `m. YY;` is missing, use `null`.
    *   `"c"`: The number from a `c. N;` entry if present (e.g., `3` from `c. 3.`). If `c. N;` is missing, use `null`.

Output MUST be ONLY the JSON object. Ensure string values are trimmed.
"""
prompt3="""
Count the number of biographical entries. An entry is identified by a bolded or capitalized surname followed by a comma, first name(s), and then typical biographical data points such as "b. [birth date]", "m. [marriage date]", "c. [children count]".

Provide only the integer count. Do not include any text, punctuation, or spaces beyond the digit itself.
"""
def prompt(text, think):
    result_prompt = prompt2
    #if(think):
    #    result_prompt = prompt_origin.replace("/no_think", "")
    return result_prompt

def prompt_asking_total_biographical():
    return prompt3