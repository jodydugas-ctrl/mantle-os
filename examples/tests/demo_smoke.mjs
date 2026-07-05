// Headless smoke tests for the two Mantle OS reference HTML demos.
//
// The Python substrate is certified by `python -m mantle prove` (83 invariants); these tests
// give the single-file *browser* demos their own runtime regression cover: each demo must mount
// with no unexpected console errors, expose its engine, and PASS its in-browser self-audit
// (Spreadsheet) / Genome+resolver checks (Reference Agent). Assertions mirror the manual
// preview-harness checks used while developing the fixes.
//
// Usage: a static server must serve examples/ at $BASE_URL (default http://localhost:8765).
//   python -m http.server 8765 --directory examples &
//   node demo_smoke.mjs
import { chromium } from "playwright";

const BASE = process.env.BASE_URL || "http://localhost:8765";
// Babel's "code generator has deoptimised ... exceeds the max of 500KB" note is emitted as a
// console.error by @babel/standalone for the large inline scripts; it is benign and expected.
const BENIGN = [/deoptimised/i, /exceeds the max of 500KB/i, /\[BABEL\]/i];

function isBenign(text) {
  return BENIGN.some((re) => re.test(text));
}

async function loadDemo(page, file, { mountSelector, waitForGlobal }) {
  const errors = [];
  page.on("console", (msg) => {
    if (msg.type() === "error" && !isBenign(msg.text())) errors.push("console: " + msg.text());
  });
  page.on("pageerror", (err) => errors.push("pageerror: " + (err && err.message)));

  await page.goto(`${BASE}/${file}?cb=${Date.now()}`, { waitUntil: "domcontentloaded", timeout: 60000 });
  // The engine globals are script/Babel-scope consts (reachable by bare name in the page realm,
  // not on window). The Reference Agent compiles a ~500KB inline TSX via in-browser Babel, so give
  // it room. A throwing predicate would reject the wait, so swallow the ReferenceError until defined.
  await page.waitForFunction(
    (g) => { try { return eval("typeof " + g) !== "undefined"; } catch (_) { return false; } },
    waitForGlobal,
    { timeout: 60000, polling: 250 }
  );
  if (mountSelector) {
    await page.waitForSelector(mountSelector, { state: "attached", timeout: 60000 });
  }
  // Surface a boot-error overlay if the demo defines one.
  const bootErr = await page.evaluate(() => {
    const e = document.getElementById("boot-err");
    return e && e.style.display === "block" ? e.textContent.slice(0, 200) : null;
  });
  if (bootErr) errors.push("boot-err: " + bootErr);
  return errors;
}

async function checkReferenceAgent(page) {
  const errors = await loadDemo(page, "Mantle_Reference_Agent.html", {
    mountSelector: "#root > *",
    waitForGlobal: "initS",
  });
  const result = await page.evaluate(() => {
    const fails = [];
    try {
      if (typeof activeBodyRefs !== "function") fails.push("activeBodyRefs missing");
      if (typeof ensureGenomeEntries !== "function") fails.push("ensureGenomeEntries missing");
      const a = initS();
      ensureGenomeEntries(a);
      a.organism = new VCW.Organism({ primeGeneration: 0, lineageIndex: {} }, VCW.Cube.genesis(VCW.standardGenome(), 0));
      // Genome present + dynamic refs (empty 003 excluded)
      const refs = activeBodyRefs(a);
      if (!refs.includes("<bodyentry.000>")) fails.push("primer ref missing from activeBodyRefs");
      if (refs.includes("<bodyentry.003>")) fails.push("empty inheritance slot wrongly referenced");
      // Dangling vs unsupported labeling
      if (resolveHydrationRef(a, "<facts.11>").reason !== "dangling-reference") fails.push("dangling ref mislabeled");
      if (resolveHydrationRef(a, "<totally_not_a_band.0>").reason !== "unsupported-reference-syntax") fails.push("unsupported ref mislabeled");
      // Self-audit carries the Genome coherence row
      const r = runStage1SelfAudit(a, (typeof HUMAN_SURFACE_MAP !== "undefined" ? HUMAN_SURFACE_MAP : []), {});
      if (!r.rows.find((x) => x.code === "B-GEN")) fails.push("B-GEN self-audit row missing");
      // Reproductive/symbiotic tissue (feasible subset): primitives present + functional
      const repro = ["mem.excrete", "mem.digest", "vault.seal", "vault.reconstruct", "egg.author", "egg.hatch"];
      const have = repro.filter((k) => typeof ZOMBIE_PRIMITIVES[k] === "function");
      if (have.length !== repro.length) fails.push("reproductive primitives missing: " + have.length + "/" + repro.length);
      const egg = ZOMBIE_PRIMITIVES["egg.author"]({ identity: { name: "t" }, truths: ["x"], commandments: ["y"] }, a).egg;
      if (ZOMBIE_PRIMITIVES["egg.hatch"]({ egg }, a).hatched !== true) fails.push("egg.hatch did not hatch");
      const v = ZOMBIE_PRIMITIVES["vault.seal"]({}, a).vault;
      if (ZOMBIE_PRIMITIVES["vault.reconstruct"]({ vault: v }, a).reconstructed !== true) fails.push("vault SELF cannot reopen its own seal");
      // Phenotype (M9): wearable SELF-encrypted app-faces — born default + express/wear round-trip + OTHER refused
      const ph = ["phenotype.express", "phenotype.list", "phenotype.wear", "phenotype.active"];
      const havePh = ph.filter((k) => typeof ZOMBIE_PRIMITIVES[k] === "function");
      if (havePh.length !== ph.length) fails.push("phenotype primitives missing: " + havePh.length + "/" + ph.length);
      if (ZOMBIE_PRIMITIVES["phenotype.active"]({}, a).active !== "origin") fails.push("default origin face not seeded");
      ZOMBIE_PRIMITIVES["phenotype.express"]({ name: "t2", source: "<b>hi</b>" }, a);
      if (ZOMBIE_PRIMITIVES["phenotype.wear"]({ name: "t2" }, a).source !== "<b>hi</b>") fails.push("phenotype.wear did not recover the sealed source");
      if (typeof openFaceCipher === "function") { try { JSON.parse(openFaceCipher("00".repeat(32), a.phenotypes.find((f) => f.name === "t2").sealed)); fails.push("OTHER opened a sealed face"); } catch (_) {} }
    } catch (e) {
      fails.push("threw: " + e.message);
    }
    return fails;
  });
  return errors.concat(result);
}

async function checkSpreadsheet(page) {
  const errors = await loadDemo(page, "Mantle_Spreadsheet_Agent.html", {
    mountSelector: null,
    waitForGlobal: "bootMantleAgent",
  });
  const result = await page.evaluate(() => {
    const fails = [];
    try {
      if (typeof bootMantleAgent !== "function") fails.push("bootMantleAgent missing");
      const audit = mantleSelfAuditV23(bootMantleAgent());
      const verdict = audit.verdict || (audit.pass ? "PASS" : "FAIL");
      if (verdict !== "PASS") fails.push("self-audit verdict = " + verdict);
      // Reproductive/symbiotic tissue (feasible subset): primitives functional via executeZombiePrimitive
      const s = bootMantleAgent();
      const egg = executeZombiePrimitive(s, "egg.author", { identity: { name: "t" }, truths: ["x"], commandments: ["y"] }).result.egg;
      if (executeZombiePrimitive(s, "egg.hatch", { egg }).result.hatched !== true) fails.push("egg.hatch did not hatch");
      const v = executeZombiePrimitive(s, "vault.seal", {}).result.vault;
      if (executeZombiePrimitive(s, "vault.reconstruct", { vault: v }).result.reconstructed !== true) fails.push("vault SELF cannot reopen its own seal");
      const p = executeZombiePrimitive(s, "mem.excrete", { entries: ["k"] }).result.plasmid;
      if (p.genesisKey !== null) fails.push("MEM plasmid is not keyless");
      // Phenotype (M9): born wearing a default face + express/wear recovers the sealed source
      if (executeZombiePrimitive(s, "phenotype.active", {}).result !== "origin") fails.push("spreadsheet default origin face not seeded");
      executeZombiePrimitive(s, "phenotype.express", { name: "t2", source: "<b>hi</b>" });
      const worn2 = executeZombiePrimitive(s, "phenotype.wear", { name: "t2" }).result;
      if (!worn2 || worn2.name !== "t2" || worn2.bytes !== 9) fails.push("spreadsheet phenotype.wear failed");
    } catch (e) {
      fails.push("threw: " + e.message);
    }
    return fails;
  });
  return errors.concat(result);
}

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  let failures = [];
  try {
    const ref = await checkReferenceAgent(page);
    console.log(ref.length ? "✗ Reference Agent:\n  " + ref.join("\n  ") : "✓ Reference Agent: mounts, Genome+resolver+self-audit OK");
    const sheet = await checkSpreadsheet(page);
    console.log(sheet.length ? "✗ Spreadsheet Agent:\n  " + sheet.join("\n  ") : "✓ Spreadsheet Agent: boots, self-audit PASS");
    failures = ref.concat(sheet);
  } finally {
    await browser.close();
  }
  if (failures.length) {
    console.error("\nDEMO SMOKE FAILED (" + failures.length + " issue(s)).");
    process.exit(1);
  }
  console.log("\nDEMO SMOKE PASSED.");
})();
