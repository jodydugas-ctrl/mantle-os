// A JavaScript twin of notes_app.py -- used to verify the language-agnostic NECROMANCY
// claim: scanner_ts (tree-sitter) must produce the same organ map as the Python scanner
// for an equivalent host, reusing the same classify_symbol unchanged.
//
// This file is a dissection FIXTURE only; it is not executed by the test suite.

const NOTES = {};
const CONFIG = { apiKey: "sk-EXAMPLEEXAMPLEEXAMPLE", store: "notes.json" };

// --- immune-ish tissue -------------------------------------------------------
function validateNote(text) {
  return Boolean(text) && text.length < 10000;
}

function checkAuthToken(token) {
  return token === CONFIG.apiKey;
}

// --- memory tissue -----------------------------------------------------------
function setNote(noteId, text) {
  NOTES[noteId] = { text, ts: Date.now() };
}

function saveNotes() {
  require("fs").writeFileSync(CONFIG.store, JSON.stringify(NOTES));
}

// --- senses tissue -----------------------------------------------------------
function handleCreateNote(request) {
  if (!validateNote(request.text || "")) {
    return { ok: false };
  }
  setNote(request.id, request.text);
  return { ok: true };
}

function onTimerTick(now) {
  return { tick: now };
}

// --- limbs tissue --------------------------------------------------------------
function sendNotification(user, message) {
  return { sentTo: user, message };
}

function renderNoteList() {
  for (const [nid, n] of Object.entries(NOTES)) {
    console.log("note " + nid + ": " + n.text.slice(0, 40));
  }
}

// --- a dormant brain affordance ---------------------------------------------------
function suggestTagsWithLlm(text) {
  return ["todo"]; // placeholder; an LLM call would live here
}

// --- the heart -----------------------------------------------------------------
function mainLoop() {
  for (let i = 0; i < 3; i++) {
    onTimerTick(Date.now());
  }
}

module.exports = {
  validateNote, checkAuthToken, setNote, saveNotes, handleCreateNote,
  onTimerTick, sendNotification, renderNoteList, suggestTagsWithLlm, mainLoop,
};
