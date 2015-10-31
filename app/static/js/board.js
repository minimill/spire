document.addEventListener('DOMContentLoaded', function() {

  // Forms
  var textForm = document.getElementById('text-form');
  var imageForm = document.getElementById('image-form');
  var boardForm = document.getElementById('board-form');

  // Inputs
  var comboInput = document.getElementById('combo');
  var filenameInput = document.getElementById('image-filename');
  var textInput = document.getElementById('text-text');
  var boardTitle = document.getElementById('board-title');

  // Slugs
  var boardSlug = document.getElementById('board-slug');
  var imageSlug = document.getElementById('image-slug');
  var textSlug = document.getElementById('text-slug');

  var images = document.getElementById('images');
  var colors = document.getElementById('colors');

  function imageTemplate(url) {
    return '<div class="image"><img src="' + url + '"></div>';
  }

  function colorTemplate(hex) {
    return '<div class="color" style="background-color: #' + hex + '">' +
      '<p>#' + hex + '</p></div>';
  }

  /**
   * Takes a form node and sends it over AJAX.
   * @param {HTMLFormElement} form - Form node to send
   * @param {function} callback - Function to handle onload.
   *                              this variable will be bound correctly.
   */
  function submitFormAjax(form, functions) {
    var url = form.action;
    var xhr = new XMLHttpRequest();

    var callbacks = {
      success: functions.success || function() {},
      error: functions.error || function(response) { console.log(response); }
    };

    var callback = function() {
      var response = JSON.parse(this.response);
      if (response.status === 'success') {
        callbacks.success(response);
      } else if (response.status === 'error') {
        callbacks.error(response);
      }
    };

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

  function getFilename(file) {
    var timestamp = new Date().toISOString();
    var extention;
    switch (file.type) {
      case 'image/png':
        extention = '.png';
        break;
      case 'image/jpeg':
        extention = '.jpg';
        break;
      case 'image/gif':
        extention = '.gif';
        break;
      case 'image/bmp':
        extention = '.bmp';
        break;
      default:
        console.log('unknown file type: ', file.type);
        extention = '.unknown';
        break;
    }
    return 'uploads/' + timestamp + extention;
  }

  function updateSlugs(slug) {
    boardSlug.value = slug;
    imageSlug.value = slug;
    textSlug.value = slug;
    boardForm.action = slug;
    textForm.action = slug + '/text/';
    imageForm.action = slug + '/image/';
  }

  function saveBoard() {
    submitFormAjax(boardForm, {
      success: function(response) {
        if (response.data.slug) {
          var title = response.data.title + ' - Spire';
          window.history.pushState({}, title, response.data.slug);
          document.title = title;
          updateSlugs(response.data.slug);
        }
      },
      error: function(response) {
        if (response.error.data.revert) {
          boardSlug.value = response.error.data.revert.slug;
          boardTitle.value = response.error.data.revert.title;
        }
      },
    });
  }

  function submitText() {
    textInput.value = comboInput.value;
    submitFormAjax(textForm, {
      success: function(response) {
        textInput.value = '';
        comboInput.value = '';
        if (response.data.image) {
          images.insertAdjacentHTML('beforeend', imageTemplate(response.data.image));
        } else if (response.data.hex) {
          colors.insertAdjacentHTML('beforeend', colorTemplate(response.data.hex));
        }
      }
    });
  }

  var myDropzone = new Dropzone('#dropzone', {
    url: 'https://minimill-spire.s3.amazonaws.com',
    thumbnailWidth: null,
    thumbnailHeight: null,
    maxThumbnailFilesize: 15,
    previewsContainer: '.dropzone-previews',
    clickable: false,
    init: function() {
      this.on('sending', function(file, xhr, formData){
        var filename = getFilename(file);
        file.previewElement.dataset.s3Filename = filename;
        formData.append('key', filename);
      });
    },
    success: function(file, response) {
      filenameInput.value = file.previewElement.dataset.s3Filename;
      submitFormAjax(imageForm, {
        success: function(response) {
          console.log(response);
        }
      });
    },
  });

  document.getElementById('dropzone').addEventListener('submit', function(e) {
    e.preventDefault();
    submitText();
    return false;
  });

  var boardInputs = boardForm.getElementsByTagName('input');
  var autoSaveTimeoutId;
  for(i=0; i<boardInputs.length; i++) {
    boardInputs[i].addEventListener('blur', function() {
      clearTimeout(autoSaveTimeoutId);
      autoSaveTimeoutId = setTimeout(saveBoard, 500);
    });
  }

});