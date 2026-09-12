# Zero to Dashboard: an HTML/CSS/JS tutorial

This is a paced route from "never written a line of front-end code" to
understanding everything in `lap-split-viewer.html`. Twelve stages. Each one
adds exactly one new idea and ends with a complete, working file you save and
open in a browser — no build tools, no installs, nothing but a text editor
and a browser tab.

**How to work through this:** for each stage, copy the code into a plain
text file, save it with the extension shown (usually `.html`), then
double-click it to open it in your browser. Change something. Save. Refresh
the browser tab. That save-refresh loop *is* front-end development — there's
no compiling, no waiting.

Don't rush stages 1–5. They're the boring plumbing everything else sits on.
Stages 9–12 is where it starts looking like the dashboard.

---

## Stage 0 — Tools

You need two things:
- A plain text editor. Not Word. VS Code, Sublime Text, or even Notepad all
  work — you just need something that saves `.txt`-style files without
  adding formatting.
- A browser. Chrome or Firefox, either is fine.

That's the whole toolchain for this tutorial.

---

## Stage 1 — HTML is just labeled boxes

HTML describes *what things are* — a heading, a paragraph, a list — not what
they look like. Save this as `stage1.html` and open it:

```html
<!DOCTYPE html>
<html>
<head>
  <title>My first page</title>
</head>
<body>
  <h1>Today's run</h1>
  <p>6.2 km, easy pace, felt good.</p>
  <ul>
    <li>Lap 1: 6:02</li>
    <li>Lap 2: 5:54</li>
  </ul>
</body>
</html>
```

Every tag opens with `<tagname>` and closes with `</tagname>`, and tags
nest inside each other like Russian dolls — `<li>` lives inside `<ul>`,
which lives inside `<body>`. That nesting is the single most important
concept in HTML. If you forget a closing tag, browsers usually still render
*something*, but it'll often be wrong in a way that's hard to spot — so get
in the habit of closing what you open, immediately, before you fill it in.

**Try it:** add a second `<p>` and a third `<li>`. Refresh. Notice nothing
has any color or spacing choices — that's not HTML's job.

---

## Stage 2 — CSS is what things look like

CSS attaches style rules to HTML elements. A rule is a **selector** (which
elements), then `{ property: value; }` pairs in curly braces.

```html
<!DOCTYPE html>
<html>
<head>
  <title>Styled page</title>
  <style>
    body {
      background: #12151b;
      color: #eae7df;
      font-family: sans-serif;
      padding: 40px;
    }
    h1 {
      color: #f0a868;
    }
    li {
      margin-bottom: 4px;
    }
  </style>
</head>
<body>
  <h1>Today's run</h1>
  <p>6.2 km, easy pace, felt good.</p>
  <ul>
    <li>Lap 1: 6:02</li>
    <li>Lap 2: 5:54</li>
  </ul>
</body>
</html>
```

`body { ... }` styles the whole page body. `h1 { ... }` styles every `<h1>`.
Colors here are **hex codes** — `#12151b` is a near-black, `#f0a868` is a
warm amber. The pattern is `#RRGGBB`, each pair a value from `00` to `ff`.
You don't need to memorize hex codes; you'll usually pick them with a color
picker or copy them from a palette you like.

**Try it:** change `#f0a868` to `red`. Change `padding: 40px` to `padding:
100px` and watch the whole page breathe out.

### Classes: styling *some* elements, not all

Tag selectors (`h1`, `li`) style *every* element of that type. Usually you
want to style specific ones. That's what `class` is for:

```html
<style>
  .warning { color: #e2665f; font-weight: bold; }
</style>

<p>Normal text.</p>
<p class="warning">This lap was way off pace.</p>
```

`.warning` (the dot means "this is a class, not a tag") only touches
elements that have `class="warning"`. This is the single most-used pattern
in real CSS: give an element a class, style the class.

---

## Stage 3 — The box model, and getting things to sit where you want

Every HTML element is a rectangle, whether you can see its edges or not.
Four layers, from the content outward:

```
┌─────────────── margin (space outside the box) ───────────────┐
│ ┌────────────── border (the box's edge) ───────────────────┐ │
│ │ ┌──────────── padding (space inside the box) ───────────┐│ │
│ │ │              content (text, image, etc.)               ││ │
│ │ └─────────────────────────────────────────────────────────┘│ │
│ └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

```html
<style>
  .card {
    background: #1a1f27;
    border: 1px solid #2a313c;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 16px;
  }
</style>

<div class="card">
  <h2>Card one</h2>
  <p>Padding pushes this text away from the card's edge.</p>
</div>
<div class="card">
  <h2>Card two</h2>
  <p>Margin pushes the cards away from each other.</p>
</div>
```

`<div>` is a generic box with no built-in meaning — it exists purely to be a
container you can style and lay out. Most of any dashboard's structure is
`<div>`s with classes.

**Try it:** set `border-radius: 12px` to `0` and see the corners go sharp.
Set `padding` to `0` and watch the text hit the edge.

---

## Stage 4 — Flexbox: lining things up

CSS's default layout stacks block elements top to bottom. To put things
side by side — like a row of stat cards — you use **flexbox**.

```html
<style>
  .row {
    display: flex;
    gap: 12px;
  }
  .stat {
    background: #1a1f27;
    border: 1px solid #2a313c;
    border-radius: 8px;
    padding: 16px;
    flex: 1;
  }
</style>

<div class="row">
  <div class="stat">Distance<br>5.26 km</div>
  <div class="stat">Time<br>33:05</div>
  <div class="stat">Avg HR<br>139 bpm</div>
</div>
```

`display: flex` on the parent turns its direct children into a row.
`gap: 12px` puts even spacing between them without needing margin tricks.
`flex: 1` on each child says "share the available space equally" — remove
it and each box shrinks to fit its own content instead.

This is exactly how the hero stat strip in the dashboard works, just with
more cells.

### Grid: the other layout tool

Flexbox is for one dimension (a row, or a column). **Grid** is for both at
once — think spreadsheet:

```html
<style>
  .grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
  }
</style>

<div class="grid">
  <div class="stat">1</div>
  <div class="stat">2</div>
  <div class="stat">3</div>
  <div class="stat">4</div>
  <div class="stat">5</div>
  <div class="stat">6</div>
</div>
```

`repeat(3, 1fr)` means "3 columns, each taking an equal fraction of the
width" — items wrap automatically onto new rows. The dashboard's hero strip
and table both lean on grid for this reason.

**Try it:** change `repeat(3, 1fr)` to `repeat(2, 1fr)` and watch it
reflow into two columns instead of three.

---

## Stage 5 — JavaScript: making the page do something

HTML is structure, CSS is appearance, JavaScript is behavior. It lives in a
`<script>` tag, usually just before `</body>` (so the page's HTML exists
before the script tries to touch it).

```html
<!DOCTYPE html>
<html>
<body>
  <h1 id="greeting">Hello</h1>
  <button id="btn">Click me</button>

  <script>
    console.log("The page loaded.");

    const button = document.getElementById("btn");
    const heading = document.getElementById("greeting");

    button.addEventListener("click", function() {
      heading.textContent = "You clicked it!";
    });
  </script>
</body>
</html>
```

Three new ideas, all load-bearing:

- **`console.log(...)`** prints to the browser's developer console (open it
  with F12, or right-click → Inspect → Console tab). This is how you'll
  debug almost everything — when something doesn't work, `console.log` the
  value you're suspicious of and look at what it actually is.
- **`document.getElementById("btn")`** reaches into the HTML and grabs the
  element with `id="btn"`, so JavaScript can read or change it. `id` is like
  `class`, but for one specific element you want to grab by name.
- **`addEventListener("click", function() { ... })`** says "when this
  happens, run this code." The function you pass in doesn't run immediately
  — it's saved and run later, whenever the click actually happens.

**Try it:** open the developer console (F12) before you click the button.
Watch `"The page loaded."` appear immediately, and nothing else until you
click.

---

## Stage 6 — Variables, arrays, objects: JavaScript's nouns

```javascript
let name = "Sarah";        // a piece of text (a "string")
let age = 34;                // a number
let isRunner = true;          // true or false (a "boolean")

let paces = [363, 354, 377]; // an array: an ordered list of values

let lap = {                  // an object: named fields, like a labeled record
  number: 1,
  pace: "6:03",
  hr: 119
};

console.log(lap.pace);       // "6:03" — dot notation reads a field
console.log(paces[0]);       // 363 — square brackets read a position, counting from 0
```

`let` declares a variable — a named slot to put a value in. `const` does the
same thing but the slot can never be reassigned later (use `const` by
default; switch to `let` only when you genuinely need to change the value).

Objects (`{ ... }`) are how you represent "one thing with several
properties" — one lap, with a number, a pace, a heart rate. Arrays (`[ ... ]`)
are how you represent "many of the same kind of thing" — six laps, one
after another. Almost all real data is an **array of objects**:

```javascript
const laps = [
  { number: 1, pace: "6:03", hr: 119 },
  { number: 2, pace: "5:54", hr: 137 },
  { number: 3, pace: "6:17", hr: 141 }
];
```

That's the exact shape your CSV data ends up in once it's parsed — and it's
the shape almost every JavaScript tool (charts, tables) expects to receive.

**Try it** in the console (F12, paste it in): type `laps[1].hr` and hit
enter. You should get `137`.

---

## Stage 7 — Loops and rendering a list to the page

You rarely write out six `<li>` tags by hand — you loop over an array and
build them.

```html
<!DOCTYPE html>
<html>
<body>
  <ul id="lap-list"></ul>

  <script>
    const laps = [
      { number: 1, pace: "6:03", hr: 119 },
      { number: 2, pace: "5:54", hr: 137 },
      { number: 3, pace: "6:17", hr: 141 }
    ];

    const list = document.getElementById("lap-list");

    let html = "";
    for (const lap of laps) {
      html += `<li>Lap ${lap.number}: ${lap.pace} @ ${lap.hr} bpm</li>`;
    }
    list.innerHTML = html;
  </script>
</body>
</html>
```

Two things to sit with:

- **`for (const lap of laps)`** runs the loop body once per item in the
  array, with `lap` holding each item in turn.
- The backtick string `` `Lap ${lap.number}: ...` `` is a **template
  literal**. Anything inside `${...}` gets evaluated and dropped into the
  string. This is how you turn data into HTML text, over and over, without
  manually gluing strings together with `+`.
- **`.innerHTML = html`** replaces everything inside an element with a
  string of HTML, which the browser then parses and displays.

This loop-and-template-literal pattern is exactly how the dashboard's table
gets built from parsed CSV rows — just with more columns per row.

**Try it:** add a fourth lap object to the array. Refresh. It should just
appear — you never touched the `<ul>` itself, only the data.

---

## Stage 8 — Getting a real file into the page

So far all your data has been typed directly into the script. Real data
comes from a file the user picks. Two pieces: a file input, and
`FileReader` to read what's inside it.

```html
<!DOCTYPE html>
<html>
<body>
  <input type="file" id="filepicker">
  <pre id="output"></pre>

  <script>
    const picker = document.getElementById("filepicker");
    const output = document.getElementById("output");

    picker.addEventListener("change", function(event) {
      const file = event.target.files[0];   // the file the user chose
      const reader = new FileReader();

      reader.onload = function(e) {
        const text = e.target.result;        // the file's contents, as text
        output.textContent = text;
      };

      reader.readAsText(file);
    });
  </script>
</body>
</html>
```

Pick any small `.txt` or `.csv` file to test this — its raw contents will
dump onto the page. `event.target.files[0]` is the file object; `FileReader`
is the browser API that actually reads the bytes off disk and hands them to
you as a string once it's done (that's why the reading happens inside
`reader.onload` — it takes a moment, so you can't just read the result on
the very next line).

Drag-and-drop is the same idea with different event names
(`dragover`/`drop` instead of `change`), which is why the dashboard file
listens for both — it just gives the user two ways to get the same file in.

---

## Stage 9 — Splitting text into rows and columns (parsing CSV)

A CSV file is just text with a very specific shape: rows separated by line
breaks, columns separated by commas. The simplest possible parser:

```javascript
const csvText = `name,pace,hr
Lap 1,6:03,119
Lap 2,5:54,137`;

const lines = csvText.split("\n");        // split into an array of rows
const header = lines[0].split(",");        // ["name", "pace", "hr"]

const rows = [];
for (let i = 1; i < lines.length; i++) {
  const values = lines[i].split(",");
  const obj = {};
  header.forEach((colName, index) => {
    obj[colName] = values[index];
  });
  rows.push(obj);
}

console.log(rows);
// [ {name: "Lap 1", pace: "6:03", hr: "119"},
//   {name: "Lap 2", pace: "5:54", hr: "137"} ]
```

`.split(",")` is doing almost all the work: cut a string into an array
wherever a character appears. The loop then zips each row's values up with
the header names to build the object shape from Stage 6.

This simple version breaks the moment a value itself contains a comma
(common in Garmin exports, which wrap every field in quotes for exactly
this reason) — which is why the real dashboard's `parseCSV` function walks
the string character by character, tracking whether it's currently "inside
quotes," rather than just calling `.split(",")`. Same goal, more careful
execution. Worth reading that function in the actual file now that you know
what problem it's solving.

---

## Stage 10 — Your first chart

Drawing a chart by hand (in `<canvas>`, with raw pixels) is a lot of work
for something like a bar chart. Almost everyone reaches for a library
instead — a chunk of pre-written JavaScript, made by someone else, that you
load into your page and call. **Chart.js** is one of the most common.

```html
<!DOCTYPE html>
<html>
<body>
  <canvas id="myChart" width="500" height="300"></canvas>

  <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js"></script>
  <script>
    const ctx = document.getElementById("myChart");

    new Chart(ctx, {
      type: "bar",
      data: {
        labels: ["Lap 1", "Lap 2", "Lap 3"],
        datasets: [{
          label: "Avg HR",
          data: [119, 137, 141]
        }]
      }
    });
  </script>
</body>
</html>
```

The first `<script src="...">` tag doesn't contain your code — it fetches
and runs *someone else's* code from the internet first, which defines a
global `Chart` function. Your own script tag, further down, then uses that
function. **Order matters**: if your script ran before the library loaded,
`Chart` wouldn't exist yet and you'd get an error — which is precisely the
bug that hit the dashboard file earlier: it pointed at a library version
that didn't actually exist at that URL, so `Chart` was never defined, and
every line trying to use it failed silently.

A `<canvas>` element is a blank rectangle Chart.js draws into. You almost
never touch it directly — you hand Chart.js your data and it does the
drawing.

**Try it:** change `type: "bar"` to `type: "line"`. Refresh. Same data,
totally different chart — the type is the only thing that changed.

---

## Stage 11 — Wiring it together: file → data → chart

Now combine Stages 8, 9, and 10: read a file, parse it, hand the result to
a chart.

```html
<!DOCTYPE html>
<html>
<body>
  <input type="file" id="filepicker" accept=".csv">
  <canvas id="myChart" width="600" height="300"></canvas>

  <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js"></script>
  <script>
    document.getElementById("filepicker").addEventListener("change", function(event) {
      const file = event.target.files[0];
      const reader = new FileReader();

      reader.onload = function(e) {
        const rows = parseCSV(e.target.result);
        drawChart(rows);
      };
      reader.readAsText(file);
    });

    function parseCSV(text) {
      const lines = text.split("\n").filter(l => l.trim().length);
      const header = lines[0].split(",");
      return lines.slice(1).map(line => {
        const values = line.split(",");
        const obj = {};
        header.forEach((col, i) => obj[col] = values[i]);
        return obj;
      });
    }

    function drawChart(rows) {
      const labels = rows.map(r => "Lap " + r.name);
      const hrValues = rows.map(r => Number(r.hr));

      new Chart(document.getElementById("myChart"), {
        type: "bar",
        data: {
          labels: labels,
          datasets: [{ label: "Avg HR", data: hrValues }]
        }
      });
    }
  </script>
</body>
</html>
```

Test it with a tiny CSV like:

```
name,pace,hr
1,6:03,119
2,5:54,137
3,6:17,141
```

Notice `.map(...)` here — it's a loop that transforms each array item into
something new and gives you back a *new* array, rather than mutating
anything. `rows.map(r => Number(r.hr))` reads as "for every row, give me
its `hr` field, turned into an actual number" — CSV values arrive as text
(`"119"`), and `Number(...)` converts that text into something you can
chart or do math on.

This — file in, parse, transform with `.map`, hand to Chart.js — is the
entire architecture of the dashboard. Everything else is more columns, more
charts, and better styling.

---

## Stage 12 — Reading the real file

You now have every idea used in `lap-split-viewer.html`. Open it in your
text editor side by side with this list and you should be able to place
every chunk:

| What you'll see in the file | Which stage taught it |
|---|---|
| `<div id="dropzone">...</div>`, nested tags | Stage 1 |
| `:root { --bg: #12151b; ... }` and `var(--bg)` | Stage 2, plus: CSS variables — define a value once at the top, reuse it everywhere with `var(--name)`, so changing the palette means editing one line instead of fifty |
| `.hero { display: grid; grid-template-columns: repeat(6, 1fr); }` | Stage 4 |
| `dropzone.addEventListener('dragover', ...)` | Stage 5 |
| `const laps = rawRows.filter(...)` | Stage 6/7 — `.filter()` is another array method like `.map()`, but it keeps only items that pass a test, instead of transforming every item |
| `function parseCSV(text) { ... }` | Stage 9 — same idea as your simple version, hardened to handle quoted fields |
| `new Chart(ctx, { type: 'bar', data: {...} })`, four separate calls | Stage 10/11 |
| `function num(v) { ... }`, `function timeToSec(v) { ... }` | small helper functions, same shape as Stage 11's `Number(r.hr)`, just handling messier real-world text like `"--"` and `"6:03"` |
| `safe(() => renderPaceHr(...), 'chartPaceHr')` | `try`/`catch` error handling — wrapping risky code so one failure doesn't take down everything after it, which is the exact bug that bit the first version of this file |

Nothing in there is a new idea at this point — it's the same dozen concepts,
just applied to 28 columns instead of 3, and with more attention paid to
things going wrong (empty cells, malformed times, missing data).

---

## Where to go from here

- **The browser console is your best debugging tool.** F12, click Console.
  Red text is an error, and it tells you the file and line number. Click
  that line number — it jumps straight to the offending code.
- **Change one thing at a time.** When something breaks, undo your last
  change before trying a different fix. It's tempting to change five things
  at once when frustrated; resist it.
- **`console.log` liberally, then delete it.** If you're not sure what a
  variable actually contains at some point, print it and look. Remove the
  log line once you've learned what you needed.
- **Copy real UI you like and ask "how would I build that."** You don't need
  to invent layouts from nothing — recognizing "oh, that's a flex row" or
  "that's a grid" in things you see day to day is most of the skill.

A concrete next exercise: take Stage 11's mini file and add a second
`<canvas>` showing pace instead of heart rate, using the `pace` column and
the `timeToSec`-style conversion from the real dashboard. That's the exact
step between "I followed a tutorial" and "I can build this myself."
