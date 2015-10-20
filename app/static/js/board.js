document.addEventListener('DOMContentLoaded', function() {

  /**
   * Takes a form node and sends it over AJAX.
   * @param {HTMLFormElement} form - Form node to send
   * @param {function} callback - Function to handle onload.
   *                              this variable will be bound correctly.
   */
  function submitFormAjax(form, callback) {
    var url = form.action;
    var xhr = new XMLHttpRequest();

    //This is a bit tricky, [].fn.call(form.elements, ...) allows us to call .fn
    //on the form's elements, even though it's not an array. Effectively
    //Filtering all of the fields on the form
    var params = [].filter.call(form.elements, function() { return true; })
    .map(function(el) {
        //Map each field into a name=value string, make sure to properly escape!
        return encodeURIComponent(el.name) + '=' + encodeURIComponent(el.value);
    }).join('&'); //Then join all the strings by &

    xhr.open("POST", url);
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");

    //.bind ensures that this inside of the function is the XHR object.
    xhr.onload = callback.bind(xhr);

    //All preperations are clear, send the request!
    xhr.send(params);
  }

  var myDropzone = new Dropzone('#dropzone', {
    url: 'http://minimill-spire.s3.amazonaws.com',
    thumbnailWidth: null,
    thumbnailHeight: null,
    maxThumbnailFilesize: 15,
    previewsContainer: '.dropzone-previews',
    clickable: false,
    init: function() {
      this.on('success', function(file, response) {
        console.log(file, response)
      });
    },
    success: function(file, response) {
      console.log(file, response);
    },
  });


  var textForm = document.getElementById('text-form');
  var textInput = document.getElementById('text');
  var comboInput = document.getElementById('combo');
  document.getElementById('dropzone').addEventListener('submit', function(e) {
    e.preventDefault();
    textInput.value = comboInput.value;
    submitFormAjax(textForm, function() {
      var response = JSON.parse(this.response);
      console.log(response);
    });
    return false;
  });

  var boardForm = document.getElementById('board-form')
  function saveBoard() {
    submitFormAjax(boardForm, function() {
      var response = JSON.parse(this.response);
      if (response.slug) {
        window.history.pushState({}, '', response.slug);
        boardForm.action = response.slug;
        textForm.action = response.slug;
        document.querySelectorAll('#board-form #slug').value = response.slug;
      }
    })
  }

  var boardInputs = boardForm.getElementsByTagName('input');
  var autoSaveTimeoutId;
  for(i=0; i<boardInputs.length; i++) {
    boardInputs[i].addEventListener('blur', function() {
      clearTimeout(autoSaveTimeoutId);
      autoSaveTimeoutId = setTimeout(saveBoard, 500);
    });
  }

});