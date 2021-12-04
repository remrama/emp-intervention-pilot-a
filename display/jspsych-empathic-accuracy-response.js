/**
 * jspsych-video-keyboard-response
 * Josh de Leeuw
 *
 * plugin for playing a video file and getting a keyboard response
 *
 * documentation: docs.jspsych.org
 *
 **/

jsPsych.plugins["empathic-accuracy-response"] = (function() {

  var plugin = {};

  jsPsych.pluginAPI.registerPreload('empathic-accuracy-response', 'stimulus', 'video');

  plugin.info = {
    name: 'empathic-accuracy-response',
    description: '',
    parameters: {
      stimulus: {
        type: jsPsych.plugins.parameterType.VIDEO,
        pretty_name: 'Video',
        default: undefined,
        description: 'The video file to play.'
      },
      choices: {
        type: jsPsych.plugins.parameterType.KEY,
        pretty_name: 'Choices',
        array: true,
        default: jsPsych.ALL_KEYS,
        description: 'The keys the subject is allowed to press to respond to the stimulus.'
      },
      prompt: {
        type: jsPsych.plugins.parameterType.STRING,
        pretty_name: 'Prompt',
        default: null,
        description: 'Any content here will be displayed below the stimulus.'
      },
      width: {
        type: jsPsych.plugins.parameterType.INT,
        pretty_name: 'Width',
        default: '',
        description: 'The width of the video in pixels.'
      },
      height: {
        type: jsPsych.plugins.parameterType.INT,
        pretty_name: 'Height',
        default: '',
        description: 'The height of the video display in pixels.'
      },
      autoplay: {
        type: jsPsych.plugins.parameterType.BOOL,
        pretty_name: 'Autoplay',
        default: true,
        description: 'If true, the video will begin playing as soon as it has loaded.'
      },
      controls: {
        type: jsPsych.plugins.parameterType.BOOL,
        pretty_name: 'Controls',
        default: false,
        description: 'If true, the subject will be able to pause the video or move the playback to any point in the video.'
      },
      start: {
        type: jsPsych.plugins.parameterType.FLOAT,
        pretty_name: 'Start',
        default: null,
        description: 'Time to start the clip.'
      },
      stop: {
        type: jsPsych.plugins.parameterType.FLOAT,
        pretty_name: 'Stop',
        default: null,
        description: 'Time to stop the clip.'
      },
      rate: {
        type: jsPsych.plugins.parameterType.FLOAT,
        pretty_name: 'Rate',
        default: 1,
        description: 'The playback rate of the video. 1 is normal, <1 is slower, >1 is faster.'
      },
      trial_ends_after_video: {
        type: jsPsych.plugins.parameterType.BOOL,
        pretty_name: 'End trial after video finishes',
        default: false,
        description: 'If true, the trial will end immediately after the video finishes playing.'
      },
      trial_duration: {
        type: jsPsych.plugins.parameterType.INT,
        pretty_name: 'Trial duration',
        default: null,
        description: 'How long to show trial before it ends.'
      },
      response_ends_trial: {
        type: jsPsych.plugins.parameterType.BOOL,
        pretty_name: 'Response ends trial',
        default: true,
        description: 'If true, the trial will end when subject makes a response.'
      }, 
      response_allowed_while_playing: {
        type: jsPsych.plugins.parameterType.BOOL,
        pretty_name: 'Response allowed while playing',
        default: true,
        description: 'If true, then responses are allowed while the video is playing. '+
          'If false, then the video must finish playing before a response is accepted.'
      }
    }
  }

  plugin.trial = function(display_element, trial) {

    // setup stimulus
    var video_html = '<div>'
    video_html += '<video id="jspsych-empathic-accuracy-response-stimulus"';

    if(trial.width) {
      video_html += ' width="'+trial.width+'"';
    }
    if(trial.height) {
      video_html += ' height="'+trial.height+'"';
    }
    if(trial.autoplay & (trial.start == null)){
      // if autoplay is true and the start time is specified, then the video will start automatically
      // via the play() method, rather than the autoplay attribute, to prevent showing the first frame
      video_html += " autoplay ";
    }
    if(trial.controls){
      video_html +=" controls ";
    }
    if (trial.start !== null) {
      // hide video element when page loads if the start time is specified, 
      // to prevent the video element from showing the first frame
      video_html += ' style="visibility: hidden;"'; 
    }
    video_html +=">";

    var video_preload_blob = jsPsych.pluginAPI.getVideoBuffer(trial.stimulus[0]);
    if(!video_preload_blob) {
      for(var i=0; i<trial.stimulus.length; i++){
        var file_name = trial.stimulus[i];
        if(file_name.indexOf('?') > -1){
          file_name = file_name.substring(0, file_name.indexOf('?'));
        }
        var type = file_name.substr(file_name.lastIndexOf('.') + 1);
        type = type.toLowerCase();
        if (type == "mov") {
          console.warn('Warning: empathic-accuracy-response plugin does not reliably support .mov files.')
        }
        video_html+='<source src="' + file_name + '" type="video/'+type+'">';   
      }
    }
    video_html += "</video>";
    video_html += "</div>";

    // add prompt if there is one
    if (trial.prompt !== null) {
      video_html += trial.prompt;
    }

    display_element.innerHTML = video_html;

    var video_element = display_element.querySelector('#jspsych-empathic-accuracy-response-stimulus');

    if(video_preload_blob){
      video_element.src = video_preload_blob;
    }

    video_element.onended = function(){
      if(trial.trial_ends_after_video){
        end_trial();
      }
      if ((trial.response_allowed_while_playing == false) & (!trial.trial_ends_after_video)) {
        // start keyboard listener
        var keyboardListener = jsPsych.pluginAPI.getKeyboardResponse({
          callback_function: after_response,
          valid_responses: trial.choices,
          rt_method: 'performance',
          persist: false,
          allow_held_key: false,
        });
      }
    }
    
    video_element.playbackRate = trial.rate;

    // if video start time is specified, hide the video and set the starting time
    // before showing and playing, so that the video doesn't automatically show the first frame
    if(trial.start !== null){
      video_element.pause();
      video_element.currentTime = trial.start;
      video_element.onseeked = function() {
        video_element.style.visibility = "visible";
        if (trial.autoplay) {
          video_element.play();
        }
      }
    }

    if(trial.stop !== null){
      video_element.addEventListener('timeupdate', function(e){
        var currenttime = video_element.currentTime;
        if(currenttime >= trial.stop){
          video_element.pause();
        }
      })
    }

    // initialize neutral rating
    var emotion_rating = 5;

    // store response
    var response_list = [];
    // also store ongoing rating, though it could be done later with the responses
    var emotion_rating_list = [emotion_rating];


    // function to end trial when it is time
    function end_trial() {

      // kill any remaining setTimeout handlers
      jsPsych.pluginAPI.clearAllTimeouts();

      // kill keyboard listeners
      jsPsych.pluginAPI.cancelAllKeyboardResponses();
      
      // stop the video file if it is playing
      // remove end event listeners if they exist
      display_element.querySelector('#jspsych-empathic-accuracy-response-stimulus').pause();
      display_element.querySelector('#jspsych-empathic-accuracy-response-stimulus').onended = function(){ };

      // gather the data to store for the trial
      var trial_data = {
        stimulus: trial.stimulus,
        responses: response_list
      };

      // clear the display
      display_element.innerHTML = '';

      // move on to the next trial
      jsPsych.finishTrial(trial_data);
    }

    // function to handle responses by the subject
    var after_response = function(info) {

      // after a valid response, the stimulus will have the CSS class 'responded'
      // which can be used to provide visual feedback that a response was recorded
      display_element.querySelector('#jspsych-empathic-accuracy-response-stimulus').className += ' responded';

      // adjust cumulative emotion rating according to response
      if ((info.key == "arrowleft") & (emotion_rating > 1)) {
        emotion_rating = emotion_rating - 1;
      } else if ((info.key == "arrowright") & (emotion_rating < 9)) {
        emotion_rating = emotion_rating + 1;
      }

      // update display prompt
      if (emotion_rating == 1) {
        document.getElementById("optionDisplay").innerHTML = "<b>1</b>  2  3  4  5  6  7  8  9";
      } else if (emotion_rating == 2) {
        document.getElementById("optionDisplay").innerHTML = "1  <b>2</b>  3  4  5  6  7  8  9";
      } else if (emotion_rating == 3) {
        document.getElementById("optionDisplay").innerHTML = "1  2  <b>3</b>  4  5  6  7  8  9";
      } else if (emotion_rating == 4) {
        document.getElementById("optionDisplay").innerHTML = "1  2  3  <b>4</b>  5  6  7  8  9";
      } else if (emotion_rating == 5) {
        document.getElementById("optionDisplay").innerHTML = "1  2  3  4  <b>5</b>  6  7  8  9";
      } else if (emotion_rating == 6) {
        document.getElementById("optionDisplay").innerHTML = "1  2  3  4  5  <b>6</b>  7  8  9";
      } else if (emotion_rating == 7) {
        document.getElementById("optionDisplay").innerHTML = "1  2  3  4  5  6  <b>7</b>  8  9";
      } else if (emotion_rating == 8) {
        document.getElementById("optionDisplay").innerHTML = "1  2  3  4  5  6  7  <b>8</b>  9";
      } else if (emotion_rating == 9) {
        document.getElementById("optionDisplay").innerHTML = "1  2  3  4  5  6  7  8  <b>9</b>";
      }

      // add response (which includes rt and button) to cumulative list
      info.rating = emotion_rating; // also include emotion rating
      response_list.push(info);

      if ((trial.response_ends_trial) | (info.key == "q")) {
        end_trial();
      }

    };

    // start the response listener
    if ((trial.choices != jsPsych.NO_KEYS) & (trial.response_allowed_while_playing)) {
      var keyboardListener = jsPsych.pluginAPI.getKeyboardResponse({
        callback_function: after_response,
        valid_responses: trial.choices,
        rt_method: 'performance',
        persist: true,
        allow_held_key: false,
      });
    }

    // end trial if time limit is set
    if (trial.trial_duration !== null) {
      jsPsych.pluginAPI.setTimeout(function() {
        end_trial();
      }, trial.trial_duration);
    }
  };

  return plugin;
})();