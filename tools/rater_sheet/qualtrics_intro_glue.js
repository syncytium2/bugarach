/* Qualtrics glue for the opening walk-through. Use a Text/Graphic question at the top of the
 * survey, with the instructions as its text. The 30-second demo plays on its own row, which is never
 * scored; Next unlocks when it ends, and Replay runs it again. */
Qualtrics.SurveyEngine.addOnload(function () {
  var q = this;
  var root = q.getQuestionContainer();
  var host = document.createElement("div");
  (root.querySelector(".QuestionBody") || root).appendChild(host);
  var replay = document.createElement("button");
  replay.type = "button";
  replay.textContent = "Replay the walk-through";
  replay.style.cssText = "margin: 10px 0; padding: 7px 12px; font: 600 14px system-ui, sans-serif; border: 1px solid #8a8a8a; border-radius: 5px; background: #f4f4f4; cursor: pointer;";
  var run = null;
  function play() {
    if (run) run.stop();
    run = RaterSheet.demo(host, RATER_DEMO.row, RATER_DEMO.event_time, function () { q.enableNextButton(); }, RATER_DEMO.lane);
  }
  replay.onclick = play;
  host.parentNode.insertBefore(replay, host.nextSibling);
  q.disableNextButton();
  play();
  Qualtrics.SurveyEngine.addOnUnload(function () { if (run) run.stop(); });
});
