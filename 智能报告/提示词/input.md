---
title: "Paper Title"
student-name: "Student Name"
affiliation: "College Name, University Name"
course: "Course Code: Course Title"
instructor: "Instructor's Name"
due-date: "Due Date"
paper-abstract: "A 250 word summary. Not indented. Remove this property entirely if abstract not required. Lorem ipsum dolor, sit amet consectetur adipisicing elit."
keywords: "Comma, Seperated, List, Of, Keywords"
---

<!-- This is a comment. It will not be exported. -->
<!-- The title will be automatically placed on the cover as well as on top of the first body page. -->
<!-- Start writing your paper from the introduction. -->

Introduction starts here. APA does not required an introction heading. Lorem ipsum dolor, sit amet consectetur adipisicing elit. Voluptates et consectetur omnis, illo veniam beatae nulla repudiandae deleniti fugiat tenetur, sit repellendus id ea placeat maiores reprehenderit.

# APA Heading 1 (Centered, bold)

Use level one headings at the start of each major section.

## APA Heading 2 (Flush left, bold)

Use level two headings at the start of each subsection.

### APA Heading 3 (Flush left, italic, bold)

Use level three headings at the start of each sub-subsection

**APA Heading 4 (Indented, bold, ends with period).** Use markdown bold syntax for level 4 headings. Paragraph following level 4 starts on the same line.

**_APA Heading 5 (Indented, italic, bold, ends with period.)_** Use markdown bold AND italic syntax together for level 5 headings. Paragraph following level 5 starts on the same line.

## Block Quote

The following is a block quote:

> Block quotes start with a `>` sign. Lorem ipsum dolor, sit amet consectetur adipisicing elit. Voluptates et consectetur omnis, illo veniam beatae nulla repudiandae deleniti fugiat tenetur.

## Math

<!-- Wrap inline math with single dollar signs  -->

This is inline math $y=2x^2$. The following is a math block.

<!-- Math blocks are wrapped in double dollar signs -->

$$
\int_a^b f(x)\,dx
$$

## Cross Referencing

Refere to section [@sec:sec1] for details.
Refer to section [@sec:sec2] for further details.

This is section [@sec:sec1].
This is section [@sec:sec2].

## Figures and Tables

Refer to figure [@fig:large-image] and table [@tbl:example-table] for details.

<!-- Wrap figures and their supporting text in fenced blocks, with custom-style set to "Figure". -->

::: { custom-style="Figure" }
**Figure [@fig:large-image]**

_Figure description in italics_

![](./large-image.png)

_Note:_ Figure notes.
:::

::: { custom-style="Figure" }

**Table [@tbl:example-table]**

_Table Description_

| Col 1 | Col2 | Col 3 |
| ----- | ---- | ----- |
| one   | two  | three |
| four  | five | six   |

:::

## Code

Inline `function hello() { print 'hello' }`

Block

```
function hello() {
  print 'hello'
}
```

---

<!-- Horizontal rules (---) are converted to page breaks. -->
<!-- Start the references section following a page break. -->
<!-- Use heading level 1 for the references title. -->
<!-- Use heading level 6 for each reference. -->

# References

###### Reference (H6) - Use heading level 6 for references. The export is setup to convert them to properly formatted APA reference with hanging indent. Lorem ipsum dolor, sit amet consectetur adipisicing elit.

###### Smith, L. A., & Mandakovic, T. (1985). Estimating: The input into good project planning. _IEEE Transactions on Engineering Management_, _EM-32_(4), 181–185. https://doi.org/10.1109/TEM.1985.6447617
