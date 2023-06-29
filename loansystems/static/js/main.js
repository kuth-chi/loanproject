
// Scripts Loading using Javascript
// const spinnerBox = document.getElementById('spinner-box');
// const dataBox = document.getElementById('data-box');
// $.ajax({
//     type: 'GET',
//     url: '/customer-json/',
//     success: function (response) {
//         setTimeout(()=> {
//         spinnerBox.classList.add('not-visible')
//             for (const i of response) {
//                 dataBox.innerHTML +=``
//             }
//         }, 500)
//     },
//     error: function (error) {
//         console.log(error)
//     }
// })


// Show toast Message TimeOut
$("#toast").delay(2000).fadeOut('slow')

// Scripts Upload and Replace Image

//  Add ToolTip Trigger List
const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))

function toggleFullScreen() {
    if (!document.fullscreenElement && !document.mozFullScreenElement && !document.webkitFullscreenElement && !document.msFullscreenElement) {
      if (document.documentElement.requestFullscreen) {
        document.documentElement.requestFullscreen();
      } else if (document.documentElement.mozRequestFullScreen) { // Firefox
        document.documentElement.mozRequestFullScreen();
      } else if (document.documentElement.webkitRequestFullscreen) { // Chrome, Safari and Opera
        document.documentElement.webkitRequestFullscreen();
      } else if (document.documentElement.msRequestFullscreen) { // IE/Edge
        document.documentElement.msRequestFullscreen();
      }
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen();
      } else if (document.mozCancelFullScreen) { // Firefox
        document.mozCancelFullScreen();
      } else if (document.webkitExitFullscreen) { // Chrome, Safari and Opera
        document.webkitExitFullscreen();
      } else if (document.msExitFullscreen) { // IE/Edge
        document.msExitFullscreen();
      }
    }
  }
  

