// *******************************
// ** important setup variables **

const EYETRACKING = false;
const FULLSCREEN = true;
const ITI = 4000; // milliseconds

const bct_length_minutes = 10; // of the whole breathing task (not including instructions)
const min_breath_gap = 1000; // ms between breaths for practice warning


const video_list = [
  {stimulus: ["ID113_vid3_crop_downsized.mp4"]},
  {stimulus: ["ID130_vid6_downsized.mp4"]},
  {stimulus: ["ID168_vid1_crop_downsized.mp4"]},
  {stimulus: ["ID174_vid3_crop_downsized.mp4"]},
  {stimulus: ["ID181_vid2_crop_downsized.mp4"]},

  {stimulus: ["ID116_vid6_downsized.mp4"]},
  {stimulus: ["ID118_vid5_crop_downsized.mp4"]},
  {stimulus: ["ID128_vid2_crop_downsized.mp4"]},
  {stimulus: ["ID131_vid1_crop_downsized.mp4"]},
  {stimulus: ["ID165_vid4_downsized.mp4"]},
];

const n_videos_total = video_list.length;
// var n_videos_a = video_list_a.length;
// var n_videos_b = video_list_b.length;
const n_videos_per_group = n_videos_total / 2;


if (CONDITION === 1 || CONDITION === 2) {
  var video_list_a = video_list.slice(0, n_videos_per_group);
  var video_list_b = video_list.slice(n_videos_per_group, n_videos_total);
} else if (CONDITION === 3 || CONDITION === 4) {
  var video_list_a = video_list.slice(n_videos_per_group, n_videos_total);
  var video_list_b = video_list.slice(0, n_videos_per_group);
};

if (CONDITION === 1 || CONDITION === 3) {
  var intermission_task = "resting";
} else if (CONDITION === 2 || CONDITION === 4) {
  var intermission_task = "bct";
};


var trial_count = 0;

const response_html_top = "<p>How did this person feel while talking?</p>";
const response_html_mid = "<pre>Very Negative           Very Positive</pre>";
var response_html_bot = "<pre id='optionDisplay'>1  2  3  4  <b>5</b>  6  7  8  9</pre>";

// *******************************

const fullscreen_on = {
  type: "fullscreen",
  fullscreen_mode: true
};
const fullscreen_off = {
  type: "fullscreen",
  fullscreen_mode: false
};


// *******************************
// ** beginning messages/trials **

const participant_info = {
  type: "survey-text",
  questions: [
    {prompt: "Enter your participant code:", name: "participant_id", required: true},
    {prompt: "Enter your email:", name: "participant_email", required: true}
  ]
};
// const rain_background_css_junk = `
//   height: 270px;
//   width: 480px;
//   text-align: center;
//   line-height: 270px;
//   background-image: url('rain.gif');
//   background-repeat: no-repeat;
//   background-position: center;
//   background-size: contain cover;
// `;
// const participant_info = {
//   type: "html-keyboard-response",
//   stimulus: `<div style="${rain_background_css_junk}"></div>`,
//   choices: jsPsych.NO_KEYS,
// };

const welcome_msg1 = `<p>Hello.</p><p>Welcome to the experiment.</p>
  <br><p>Please make sure your sound is on.</p>
  <p>Do not use the Back button of your browser during this experiment.</p><br><br>`;
const welcome_msg2 = `<p>This experiment will take roughly
  30-45 minutes to complete.</p>
  <p>You will mostly be watching 2-minute videos and rating the speaker's emotions.</p>
  <p>Between two sets of 5 videos, you will be asked to spend
  10-12 minutes on a different task.</p>
  <br><p>The experiment is not complete until you are redirected to our lab webpage.</p>
  <br><br>`;

const welcome_messages = {
  type: "instructions",
  pages: [welcome_msg1, welcome_msg2],
  show_clickable_nav: true,
  button_label_previous: "Previous",
  button_label_next: "Continue"
};
const welcome_sequence = {
  timeline: [participant_info, welcome_messages]
};



// var prevideo = {
//   type: "html-button-response",
//   stimulus: function() {
//     trial_count++;
//     var msg = "<p>Continue to watch video " + trial_count + "/" + n_videos + ".</p><br><br>";
//     return msg;
//   },
//   choices: ["Continue"]
// };

const preload_all_videos = {
  type: "preload",
  auto_preload: true // automatically load all files based on the main timeline
};


const empathy_instructions = {
  type: "html-button-response",
  stimulus: `<p>As you watch the following ${n_videos_per_group} videos,<br>
    rate how positive or negative you believe the speaker is feeling.<br>
    Adjust your ratings as needed throughout the entire video.<br>
    <br><p>Use the left and right buttons to adjust your response on this scale.</p>
    ${response_html_mid}${response_html_bot}<br><br>`,
  choices: ["Begin"],
  data: {phase:"empathy-intro"},
  post_trial_gap: 1000,
};

const empathy_prevideo = {
  type: "html-keyboard-response",
  stimulus: function() {
    trial_count++;
    // if (trial_count > n_videos_per_group) {
    //   trial_count = 1;
    // };
    const msg = `<p>Video ${trial_count}/${n_videos_total} will begin
      in <span id='clock'>0:00</span></p>`;
    return msg;
  },
  choices: jsPsych.NO_KEYS,
  trial_duration: ITI+250,
  data: {phase:"empathy-intro"},
  on_load: function(){
    // var wait_time = 1 * 60 * 1000; // in milliseconds
    var wait_time = ITI; // in milliseconds
    var start_time = performance.now();
    var interval = setInterval(function(){
      var time_left = wait_time - (performance.now() - start_time);
      var minutes = Math.floor(time_left / 1000 / 60);
      var seconds = Math.floor((time_left - minutes*1000*60)/1000);
      var seconds_str = seconds.toString().padStart(2,'0');
      document.querySelector('#clock').innerHTML = minutes + ':' + seconds_str
      if(time_left <= 0){
        document.querySelector('#clock').innerHTML = "0:00";
        clearInterval(interval);
      }
    }, 250)
  }
};



const extensions = [];

if (EYETRACKING) {
  var webgazer_ext = {
    type: "webgazer", 
    params: { targets: [
        "#jspsych-empathic-accuracy-response-stimulus",
        "#optionDisplay"
      ] }
  };
  extensions.push(webgazer_ext);
};


const empathy_task_trial = {
  type: "empathic-accuracy-response",
  prompt: response_html_top + "<br>" + response_html_mid + response_html_bot,
  stimulus: jsPsych.timelineVariable("stimulus"),
  width: 600,
  // height: 200,
  choices: ["arrowleft", "arrowright"],
  response_allowed_while_playing: true,
  response_ends_trial: false,
  trial_ends_after_video: true,
  rate: 1,
  autoplay: true,
  data: {phase:"empathy-test"},
  extensions: extensions
};

const empathy_procedure_a = {
  timeline: [empathy_prevideo, empathy_task_trial],
  timeline_variables: video_list_a,
  randomize_order: false,
  repetitions: 1
};

const empathy_procedure_b = {
  timeline: [empathy_prevideo, empathy_task_trial],
  timeline_variables: video_list_b,
  randomize_order: false,
  repetitions: 1,
  // on_timeline_start: function() {
  //     trial_count++;
  //     console.log(trial_count);
  // },
  // on_timeline_finish: function() {
  //     console.log("Block ended, breath count at ", breath_count);
  // }
};




// *******************************
// ** BCT BCT BCT BCT BCT stuff **
//
// a trial is made of an html-keyboard-response
// and a response handler functions



/**********  BREATH COUNTING TASK VARIABLES  ***************/

const bct_html = "<p style='font-size:60px'>+</p>";
// var bct_html = `<iframe src="https://giphy.com/embed/dI3D3BWfDub0Q" width="480" height="270" frameBorder="0"></iframe>`;
const resting_html = `<iframe src="rain.gif" width="480" height="270" frameBorder="0"></iframe>`;

const bct_length_ms = bct_length_minutes*60*1000;

const bct_response_keys = ["arrowdown", "arrowright", " "];

const bct_feedback_html = `<p>You responded either incorrectly or too fast.</p>
  <p>Let's restart the counter.</p>
  <p>Make sure you press <code>&downarrow;</code> only once for each exhale,<br>
  and then press <code>&rightarrow;</code> on the 9th exhale.</p><br><br>`;

const bct_msg1 = `<p>In the next task, we would like you to be aware of your breath.<p>
  <p>Please be aware of the movement of breath in and out
  <br>in the space below your nose and above your upper lip
  <br>(or any other aspect of your breath).<p>
  <p>There's no need to control the breath.
  <br>Just breathe at a comfortable slow pace.</p>
  <br><br>`;
const bct_msg2 = `<p>At some point, you may notice
  <br>your attention has wandered from the breath.</p>
  <p>That's okay. Just gently place it back on the breath.</p>
  <br><br>`;
const bct_msg3 = `<p>To help attention stay with the breath,<br>
  you'll use a small part of your attention<br>
  to silently count breaths from 1 to 9, again and again.</p>
  <p>An in and out breath together makes one count.<br>
  Say the count softly in your mind so it only gets a little attention<br>
  while most of the attention is on feeling the breath.</p>
  <p>Press the Down Arrow (<code>&downarrow;</code>) with breaths 1-8,<br>
  and the Right Arrow (<code>&rightarrow;</code>) with breath 9.</p>
  <p>This means you'll be pressing a button with each breath.</p><br><br>`;
const bct_msg4 = `<p>If you find that you have forgotten the count,<br>
  just press the spacebar and restart the count at 1 with the next breath.</p>
  <p>Do not count the breaths using your fingers but only in your head.</p><br><br>`;
const bct_msg5 = `<p>We suggest you sit in an upright,<br>
  relaxed posture that feels comfortable.</p>
  <p>Please keep your eyes at least partly open<br>
  and resting on the screen during the experiment.</p><br><br>`;
const bct_msg6 = `<p>Press the <code>&downarrow;</code> key.</p><br><br>`;
const bct_msg7 = `<p>Press the <code>&rightarrow;</code> key.</p><br><br>`;
const bct_msg8 = `<p>Press the spacebar.</p><br><br>`;
const bct_msg9 = `<p>Great!</p>
  <p>The task will begin now.</p>
  <p>The screen will only show a centered cross<br>
  but your presses will be registered.<br>
  A message will appear on screen to let<br>
  you know when this task is over.</p>
  <p>The task will last for ${bct_length_minutes} minutes,<br>
  no matter what pace your breathe or how accurate you are.</p>
  <p>Remember to sit in a comfortable position,<br>
  focus primarily on your breathing,<br>
  and you can press spacebar to reset<br>
  the counter if you get lost.</p><br><br>`;

const bct_closing_msg = `<p>Finished!</p>
  <p>No more counting your breaths. &#128578;</p><br><br>`;

const bct_instructions = {
  type: "instructions",
  pages: [bct_msg1, bct_msg2, bct_msg3, bct_msg4, bct_msg5],
  show_clickable_nav: true,
  allow_keys: false,
  data: {phase:"bct-intro"},
  button_label_previous: "Previous",
  button_label_next: "Continue"
};
const bct_button_checks = {
  type: "html-keyboard-response",
  data: {phase:"bct-intro"},
  timeline: [
    {stimulus: bct_msg6, choices: ["arrowdown"]},
    {stimulus: bct_msg7, choices: ["arrowright"]},
    {stimulus: bct_msg8, choices: [" "]},
  ]
};
const pre_bct_countdown = {
  type: "html-button-response",
  stimulus: bct_msg9,
  choices: ["Begin"],
  data: {phase:"bct-intro"},
  post_trial_gap: 1000,
};

const bct_closing_screen = {
  type: "html-button-response",
  choices: ["Continue"],
  stimulus: bct_closing_msg,
  data: {"phase":"bct-outro"}
};

var breath_count = 0;
function bct_response_handler(data) {
  let breath_correct = true;
  if (data.response) { //null in the one case of a trial being cutoff at the end
    if (jsPsych.pluginAPI.compareKeys(data.response, " ")) {
      breath_count = 0;
      breath_correct = false;
    } else if (jsPsych.pluginAPI.compareKeys(data.response, "arrowdown")) {
      breath_count++;
      if (breath_count >= 9) {
        breath_correct = false;
      };
    } else if (jsPsych.pluginAPI.compareKeys(data.response, "arrowright")) {
      if (breath_count != 8) {
        breath_correct = false;
      };
      breath_count = 0;
    };

    // if it's practice
    // and incorrect or RT is too fast, (but not on first breath)
    // reset the counter for display purposes
    if (data.phase=="bct-practice") {
      if ((data.rt < min_breath_gap) & (breath_count > 1)) {
        breath_correct = false;
      };
      if (!breath_correct) {
        breath_count = 0;
      };
    };
    
    data.correct = breath_correct;
  };
};

const bct_arrow_rows = [
  "<pre style='opacity:0.5;'>&downarrow; &downarrow; &downarrow; &downarrow; &downarrow; &downarrow; &downarrow; &downarrow; &rightarrow;</pre>",
  "<pre>&downarrow;<span style='opacity:0.5;'> &downarrow; &downarrow; &downarrow; &downarrow; &downarrow; &downarrow; &downarrow; &rightarrow;</span></pre>",
  "<pre>&downarrow; &downarrow;<span style='opacity:0.5;'> &downarrow; &downarrow; &downarrow; &downarrow; &downarrow; &downarrow; &rightarrow;</span></pre>",
  "<pre>&downarrow; &downarrow; &downarrow;<span style='opacity:0.5;'> &downarrow; &downarrow; &downarrow; &downarrow; &downarrow; &rightarrow;</span></pre>",
  "<pre>&downarrow; &downarrow; &downarrow; &downarrow;<span style='opacity:0.5;'> &downarrow; &downarrow; &downarrow; &downarrow; &rightarrow;</span></pre>",
  "<pre>&downarrow; &downarrow; &downarrow; &downarrow; &downarrow;<span style='opacity:0.5;'> &downarrow; &downarrow; &downarrow; &rightarrow;</span></pre>",
  "<pre>&downarrow; &downarrow; &downarrow; &downarrow; &downarrow; &downarrow;<span style='opacity:0.5;'> &downarrow; &downarrow; &rightarrow;</span></pre>",
  "<pre>&downarrow; &downarrow; &downarrow; &downarrow; &downarrow; &downarrow; &downarrow;<span style='opacity:0.5;'> &downarrow; &rightarrow;</span></pre>",
  "<pre>&downarrow; &downarrow; &downarrow; &downarrow; &downarrow; &downarrow; &downarrow; &downarrow;<span style='opacity:0.5;'> &rightarrow;</span></pre>",
  "<pre>&downarrow; &downarrow; &downarrow; &downarrow; &downarrow; &downarrow; &downarrow; &downarrow; &rightarrow;</pre>",
];

function bct_generate_prompt_html() {
  const arrows = bct_arrow_rows[breath_count];
  if (breath_count == 0) {
    // a space just so the fixation doesn't bounce around
    var count_str = "<pre> </pre>";
  } else {
    var count_str = "<pre>" + breath_count.toString() + "</pre>";
  };
  return arrows + count_str
};

const bct_conditional_feedback_display = {
  timeline: [
    {
      type: "html-button-response",
      data: {phase:"bct-practice"},
      stimulus: bct_feedback_html,
      choices: ["Restart"],
    }
  ],
  conditional_function: function() {
    const data = jsPsych.data.getLastTrialData().values()[0];
    // show if NOT correct, unless they pressed spacebar
    return (!(data.correct) & !(jsPsych.pluginAPI.compareKeys(data.response, " ")));
  },
};

var bct_correct_practice_counter = 0;
function bct_check_if_repeat_practice() {
  // only move on if correct on the 9th right arrow press
  // for the SECOND time
  //
  // this is where the warning is coming from.
  // response is sometimes a 0 bc it comes from the button response
  // from Restarting after feedback. It's a deprecation warning
  // about comparing keycodes, safe to ignore.
  const response = jsPsych.data.getLastTrialData().values()[0].response;
  const correct = jsPsych.data.getLastTrialData().values()[0].correct;
  if (correct & (jsPsych.pluginAPI.compareKeys(response, "arrowright"))) {
    bct_correct_practice_counter++;
  };
  if (bct_correct_practice_counter == 2) {
    return false; // dont repeat
  } else {
    return true; // DO IT AGAINNNNN
  }
};


const bct_practice1_procedure = {
  timeline: [
    { // BCT response collection, resets if wrong and displays feedback
      type: "html-keyboard-response",
      stimulus: "<p>Let's practice.</p>"
        + "<p>Breath at a comfortable slow pace through your nose"
        + "<br>while pressing <code>&downarrow;</code> on breaths 1-8 and <code>&rightarrow;</code> on 9.</p>"
        + "<p>Remember you can press the spacebar at any time to reset the counter.</p>"
        + bct_html,
      choices: bct_response_keys,
      response_ends_trial: true,
      on_finish: bct_response_handler,
      data: {phase:"bct-practice"},
      // data: { //this stuff gets ADDED to the trial data structure
      //   "practice": true
      // },
      prompt: bct_generate_prompt_html
    },
    bct_conditional_feedback_display
  ],
  loop_function: bct_check_if_repeat_practice
  // on_timeline_start: function() {
  //   trial_count++;
  //   console.log(trial_count);
  // },
  // on_timeline_finish: function() {
  //     console.log("Block ended, breath count at ", breath_count);
  // }
};

const bct_mid_practice_screen = {
  type: "html-button-response",
  data: {phase:"bct-practice"},
  stimulus: `<p>Great!</p>
    <p>Now try repeating the same process without visual feedback.</p>
    <p>You will only see a cross in the center of the screen while
    <br>you count your breaths and press the buttons as before.</p>
    <p>But don't worry, your presses are registered.</p>
    <br><br>`,
  choices: ["Begin"],
};

const bct_reset_practice_trial_counter = {
  type: "call-function",
  data: {phase:"bct-practice"},
  func: function() {
  // reset this from the first practice round
  // (this means it takes the same amount of correct trials)
    bct_correct_practice_counter = 0;
  },
};

const bct_practice2_procedure = {
  timeline: [
    { // BCT response collection, resets if wrong
      // (same as practice1 but without prompt)
      type: "html-keyboard-response",
      stimulus: bct_html,
      choices: bct_response_keys,
      response_ends_trial: true,
      on_finish: bct_response_handler,
      data: {phase:"bct-practice"}
    },
    bct_conditional_feedback_display
  ],
  loop_function: bct_check_if_repeat_practice
};

const bct_response = {
  type: "html-keyboard-response",
  stimulus: bct_html,
  choices: bct_response_keys,
  response_ends_trial: true,
  on_finish: bct_response_handler,
  data: {
    phase: "bct-test",
    breath_count: function() {
      return breath_count;
    }
  }
};


function bct_timer_init() {
  setTimeout(function(){
    jsPsych.endCurrentTimeline();
    // jsPsych.finishTrial();
  }, bct_length_ms);
};


const start_bct_timer = {
  type: "call-function",
  data: {phase:"bct-practice"},
  func: bct_timer_init
};

const infinite_bct_loop = {
  timeline: [bct_response],
  repetitions: 10000, // an arbitrarily high number of trials
};


// full BCT timeline with practice and task
const full_bct = {
  timeline: [
    bct_instructions,
    bct_button_checks,
    bct_practice1_procedure,
    bct_mid_practice_screen,
    bct_reset_practice_trial_counter,
    bct_practice2_procedure,
    pre_bct_countdown,
    start_bct_timer,
    infinite_bct_loop,
    bct_closing_screen,
  ]
};


/////////// end BCT stuff
////////////////////////////////////////////////



// *******************************
// *******************************

////////////// resting (control) task
const resting_prompt = `<p>Please remain relaxed with<br>
  eyes open for the following ${bct_length_minutes} minute period.</p>
  <p>Feel free to let your mind wander,<br>
  just don't fall asleep</p>
  <p>A short video will loop the entire time.<br>
  and the screen will advance when time is up.</p>`;

const resting_instructions = {
  type: "html-button-response",
  stimulus: resting_prompt,
  choices: ["Continue"],
  data: { phase:"resting-intro" }
};

const resting_closing_msg = `<p>Finished!</p>
  <p>&#128578;</p><br><br>`;

const resting_closing_screen = {
  type: "html-button-response",
  stimulus: resting_closing_msg,
  choices: ["Continue"],
  data: {phase:"resting-outro"}
};

const resting_task = {
  type: "html-keyboard-response",
  stimulus: resting_html,
  choices: jsPsych.NO_KEYS,
  trial_duration: bct_length_ms,
  data: { phase: "resting-test" }
};


const full_resting = {
  timeline: [
    resting_instructions,
    resting_task,
    resting_closing_screen
  ]
};
  
// var intervention = {
//   type: "video-button-response",
//   stimulus: ["rain-10m.mp4"],
//   width: 600,
//   choices: ["Continue"],
//   response_allowed_while_playing: false,
//   response_ends_trial: true,
//   trial_ends_after_video: false,
//   rate: 1,
//   autoplay: true
// };

const final_msg = {
  type: "html-button-response",
  stimulus: `<p>&#128524;<br>
    Thank you for your participation</p>
    <p>Continue to complete the experiment and exit.<br>`,
  choices: ["Finish"],
};


if (EYETRACKING) {
  var init_camera_trial = {
    type: "webgazer-init-camera"
  };
  var calibration_trial = {
    type: "webgazer-calibrate",
  };
  var validation_trial = {
    type: "webgazer-validate",
    data: {
      task: "validate"
    }
  };
  var camera_instructions = {
    type: "html-button-response",
    stimulus: `
      <p>In order to participate you must allow the experiment to use your camera.</p>
      <p>You will be prompted to do this on the next screen.</p>
      <p>If you do not wish to allow use of your camera, you cannot participate in this experiment.<p>
      <p>It may take up to 30 seconds for the camera to initialize after you give permission.</p>
    `,
    choices: ["Continue"],
  };
  var calibration_instructions = {
    type: "html-button-response",
    stimulus: `
      <p>Now you'll calibrate the eye tracking, so that the software can use the image of your eyes to predict where you are looking.</p>
      <p>You'll see a series of dots appear on the screen. Look at each dot and click on it.</p>
    `,
    choices: ["Continue"],
    post_trial_gap: 1000
  };
  var validation_instructions = {
    type: "html-button-response",
    stimulus: `
      <p>Now we'll measure the accuracy of the calibration.</p>
      <p>Look at each dot as it appears on the screen.</p>
      <p style="font-weight: bold;">You do not need to click on the dots this time.</p>
    `,
    choices: ["Continue"],
    post_trial_gap: 1000
  };
  var recalibrate_instructions = {
    type: "html-button-response",
    stimulus: `
      <p>The accuracy of the calibration is a little lower than we'd like.</p>
      <p>Let's try calibrating one more time.</p>
      <p>On the next screen, look at the dots and click on them.<p>
    `,
    choices: ["OK"],
  };
  var recalibrate = {
    timeline: [recalibrate_instructions, calibration_trial,
      validation_instructions, validation_trial],
    conditional_function: function(){
      const validation_data = jsPsych.data.get().filter({task: "validate"}).values()[0];
      return validation_data.percent_in_roi.some(function(x){
        const minimum_percent_acceptable = 50;
        return x < minimum_percent_acceptable;
      });
    },
    data: {
      phase: "recalibration"
    }
  };
  var calibration_done = {
    type: "html-button-response",
    stimulus: `
      <p>Great, we're done with calibration!</p>
    `,
    choices: ["Continue"]
  };

};


const timeline = [];

timeline.push(preload_all_videos);
timeline.push(welcome_sequence);

if (FULLSCREEN) {
  timeline.push(fullscreen_on);
};

if (EYETRACKING) {
  timeline.push(camera_instructions);
  timeline.push(init_camera_trial);
  timeline.push(calibration_instructions);
  timeline.push(calibration_trial);
  timeline.push(validation_instructions);
  timeline.push(validation_trial);
  timeline.push(recalibrate);
  timeline.push(calibration_done);
};

timeline.push(empathy_instructions);
timeline.push(empathy_procedure_a);

if (intermission_task === "resting") {
  timeline.push(full_resting);
} else if (intermission_task === "bct") {
  timeline.push(full_bct);
};

timeline.push(empathy_instructions);
timeline.push(empathy_procedure_b);

timeline.push(final_msg);

if (FULLSCREEN) {
  timeline.push(fullscreen_off);
};

// var full_trial = {
//   timeline: [wait_for_button],
// }

// build timeline
// timeline.push(preload);
// timeline.push(timer_start);
// timeline.push(soundtest);
// timeline.push(play_sound);
// // timeline.push(wait_for_button);
// // timeline.push(feedback_text);
// timeline.push(full_trial);

// timeline.push(if_node)
// timeline.push(fullscreen_off);
jsPsych.init({
  timeline: timeline,
  extensions: [
    {type: "webgazer"}
  ],
  exclusions: {
    audio: true
  },
  on_finish: function() {
    // jsPsych.data.displayData("json");
    window.location.href = "https://pallerlab.psych.northwestern.edu/"
    // jsPsych.data.get().localSave("csv", "sample.csv");
    // jsPsych.endExperiment("Experiment is over. Thank you.")
  }
});