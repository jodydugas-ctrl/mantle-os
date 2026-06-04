# Publishing Mantle OS to GitHub — step by step (web, no git required)

This guide gets your Mantle OS project onto GitHub using only the website — no command line.
Your GitHub username is **jodydugas-ctrl**.

> This file is just for you. You do **not** need to upload it to the repo (you can, but it's
> optional). The files that make up the actual project are everything else in this folder.

---

## Step 0 — Make sure the project folder is complete

In your `Mantle` folder you should have:

- The documents: `Mantle_PRIMER.md`, `Mantle_Doctrine.md`, `Mantle_Organism_Lens.md`,
  `Mantle_Organ_Atlas.md`, `Mantle_Part1_Body.md`, `Mantle_Part1_Body_Audit.md`,
  `Mantle_Part2_Mind.md`, `Mantle_Part2_Mind_Audit.md`, `Mantle_Assimilator.md`,
  `Mantle_Extensions.md`
- The folders: `vcw/`, `doctrine/`, `examples/`
- The new scaffolding I added: `README.md`, `LICENSE`, `.gitignore`, `CONTRIBUTING.md`

> Tip: delete the `vcw/__pycache__/` folder before uploading if it's present — it's auto-generated
> Python cache and the `.gitignore` already excludes it.

---

## Step 1 — Create the repository

1. Go to **https://github.com/new** (you're already signed in as jodydugas-ctrl).
2. **Repository name:** `mantle-os` (lowercase, no spaces).
3. **Description** (optional): `An organic coding framework — grow software like a living organism, then give it a mind.`
4. **Visibility:** choose **Public** (this is meant to be an open-source demo).
5. **Important:** leave **all three "Initialize this repository" checkboxes UNCHECKED**
   (do *not* add a README, .gitignore, or license here — you already have them in your folder, and
   adding them now would create conflicts).
6. Click **Create repository**.

You'll land on a mostly empty page with setup instructions. Ignore the command-line instructions.

---

## Step 2 — Upload your files

1. On that new repository page, find the link **"uploading an existing file"**
   (it's in the line: *"…or push an existing repository… or uploading an existing file"*).
   Or go directly to: `https://github.com/jodydugas-ctrl/mantle-os/upload/main`
2. Open your `Mantle` folder on your computer in a File Explorer window.
3. **Select everything** in the folder (Ctrl+A), then **drag it all** onto the GitHub upload area
   that says *"Drag files here to add them to your repository."*
   - Dragging whole folders (`vcw`, `doctrine`, `examples`) preserves the folder structure
     automatically — GitHub keeps the paths.
   - Make sure the hidden file `.gitignore` is included. In Windows File Explorer, enable
     **View → Show → Hidden items** so you can see and select it.
4. Wait for all files to finish uploading (you'll see them listed).

> GitHub's web uploader handles up to 100 files per drag and 25 MB per file. Your largest file is
> about 0.5 MB, so you're well within limits. If you have more than 100 files for any reason,
> upload in two drags (the second drag adds to the first).

---

## Step 3 — Commit

1. Scroll to the bottom to the **"Commit changes"** box.
2. In the first field, type a short message like: `Initial commit: Mantle OS v2.3`.
3. Leave **"Commit directly to the main branch"** selected.
4. Click **Commit changes**.

Done. Your repository is now live at:

**https://github.com/jodydugas-ctrl/mantle-os**

---

## Step 4 — Check it looks right

- The repo's front page should display your `README.md` automatically.
- Click into `vcw/`, `doctrine/`, and `examples/` to confirm the files are inside their folders.
- The license should show as **MIT** near the top-right of the repo page.

---

## Optional polish (after it's up)

- **Add topics:** On the repo page, click the gear next to "About" and add topics like
  `ai`, `framework`, `llm`, `agents`, `organic-coding`. This helps people discover it.
- **Add the description and website** in that same "About" box.
- **Pin it** to your profile so visitors see it first.

---

## If something goes wrong

- **"main branch doesn't exist yet"** when visiting the `/upload/main` URL: just use the
  "uploading an existing file" link on the repo's landing page instead.
- **A file won't upload:** check it isn't over 25 MB. The whole project here is far under that.
- **You accidentally initialized with a README:** that's fine — when you upload your own
  `README.md`, GitHub will ask; choose to replace, or rename one. Easiest fix is to delete the repo
  (Settings → bottom → Delete) and start again with the checkboxes unchecked.

---

## Want to use git later?

Web upload is perfect for getting started. When you're ready to make frequent changes, installing
**GitHub Desktop** (https://desktop.github.com) gives you a friendly visual app — no command line —
to sync changes between your computer and GitHub. That's a good next step once the repo is up.
