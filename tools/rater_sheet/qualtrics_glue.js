/* Qualtrics glue. The question is a Text Entry question inside a Loop & Merge block whose
 * Field 1 is the row id, and whose text contains <span class="rater-row">${lm://Field/1}</span>.
 * The script hides the text box and writes one self-describing line into it, so the export
 * needs no column map: row=r07;judge=probably_real;marks=31.2,52.0
 * Next stays disabled until the real-or-synthetic question is answered. */
Qualtrics.SurveyEngine.addOnload(function () {
  var q = this;
  var root = q.getQuestionContainer();
  var idEl = root.querySelector(".rater-row");
  var id = idEl ? (idEl.textContent || "").trim() : "";
  if (idEl) idEl.style.display = "none";
  var input = root.querySelector("input[type=text], textarea");
  if (input) input.style.display = "none";
  var host = document.createElement("div");
  (root.querySelector(".QuestionBody") || root).appendChild(host);
  var row = RATER_ROWS[id];
  if (!row) {
    host.textContent = "This row could not be loaded (row id '" + id + "'). Please tell the person who sent the survey.";
    return;
  }
  q.disableNextButton();
  function write(value) {
    if (!input) return;
    var proto = input.tagName === "TEXTAREA" ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
    var setter = Object.getOwnPropertyDescriptor(proto, "value").set;
    setter.call(input, value);                       // so a React-driven page sees the change
    input.dispatchEvent(new Event("input", {bubbles: true}));
    input.dispatchEvent(new Event("change", {bubbles: true}));
  }
  var sheet = RaterSheet.mount(host, row, function (state) {
    write(RaterSheet.encode(state));
    if (state.judge) q.enableNextButton(); else q.disableNextButton();
  });
  Qualtrics.SurveyEngine.addOnUnload(function () { sheet.destroy(); });
});
