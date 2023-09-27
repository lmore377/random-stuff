freq = 0
backend_host = "127.0.0.1"

function sysBL() {
  val = document.getElementById("sys_bl").value
  fetch('http://' + backend_host + ':8000/set', {
    method: 'POST',
    body: JSON.stringify({
      param: 'sysBL',
      value: val
    })
  })
    .then(response => response.json())
    .then(json => console.log(json));
}

function knobFreq(event) {
  const delta = Math.sign(event.deltaX);
  fnum = document.querySelector('input[name="freq_digit"]:checked').value;
  if (delta == -1) {
    if ((freq - fnum) >= 0) {
      freq -= fnum;
      padded = String(freq).padStart(10, '0');;
      document.getElementById("freq_display").value = padded;
    }
  } else {
    freq = parseInt(freq) + parseInt(fnum);
    padded = String(freq).padStart(10, '0');;
    document.getElementById("freq_display").value = padded;
  }
  out = document.getElementById("freq_display").value;
  fetch('http://' + backend_host + ':8000/set', {
    method: 'POST',
    body: JSON.stringify({
      param: 'freq',
      value: freq
    })
  })
    .then(response => response.json())
    .then(json => console.log(json));
}

function knobMode(event) {
  const delta = Math.sign(event.deltaX);
  var select = document.getElementById("mode");
  if (delta == 1) {
    if (select.options.selectedIndex < 11) {
      select.options.selectedIndex++;
    }
  } else {
    if (select.options.selectedIndex > 0) {
      select.options.selectedIndex--;
    }
  }
  out = document.getElementById("freq_display").value;
  fetch('http://' + backend_host + ':8000/set', {
    method: 'POST',
    body: JSON.stringify({
      param: 'demod',
      value: select.value
    })
  })
    .then(response => response.json())
    .then(json => console.log(json));
}

function knobSysBL(event) {
  const delta = Math.sign(event.deltaX);
  val = document.getElementById("sys_bl").value;
  if (delta == -1) {
    if (val >= 1) {
      document.getElementById("sys_bl").value = parseInt(val) - parseInt(3);
    }
  } else {
    document.getElementById("sys_bl").value = parseInt(val) + parseInt(4);
  }
  sysBL();
}

window.addEventListener("wheel", event => {
  knob_mode = document.querySelector('input[name="knob_mode"]:checked').value;
  if (knob_mode == "freq") {
    knobFreq(event);
  }
  else if (knob_mode == "mode") {
    knobMode(event);
  }
  else if (knob_mode == "sysbl_knob") {
    knobSysBL(event);
  }
});

window.addEventListener("change", event => {
  if (event.target.name == "mode") {
    mode = event.target.value;
    fetch('http://' + backend_host + ':8000/set', {
      method: 'POST',
      body: JSON.stringify({
        param: 'demod',
        value: mode
      })
    })
      .then(response => response.json())
      .then(json => console.log(json));
  }
});

setInterval(function () {
  autorefresh = document.getElementById('autorefresh').checked;
  if (autorefresh) {
    fetch('http://' + backend_host + ':8000/get?param=all', {
      method: 'GET',
    })
      .then(response => response.json())
      .catch(error => console.log(error))
      .then(response => {
        freq = String(response.freq).padStart(10, '0');
        mode = String(response.mode);
        passband = String(response.passband);
        strength = String(response.strength);
        squelch = String(response.squelch);
        document.getElementById("freq_display").value = freq;
        document.getElementById("mode").value = mode;
      })
  }
}, 250);

function switchTab(evt, tabName) {
  var i, tabcontent, tablinks;
  tabcontent = document.getElementsByClassName("tabcontent");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }
  tablinks = document.getElementsByClassName("tablinks");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" active", "");
  }
  document.getElementById(tabName).style.display = "block";
  evt.currentTarget.className += " active";
}
