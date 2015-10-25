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

  // Forms
  var textForm = document.getElementById('text-form');
  var imageForm = document.getElementById('image-form');

  // Inputs
  var comboInput = document.getElementById('combo');
  var filenameInput = document.getElementById('image-filename');
  var textInput = document.getElementById('board-text');

  // Slugs
  var boardSlug = document.getElementById('board-slug');
  var imageSlug = document.getElementById('image-slug');
  var textSlug = document.getElementById('text-slug');

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
      submitFormAjax(imageForm, function() {
        var response = JSON.parse(this.response);
        console.log(response);
      });
    },
  });

  function updateSlugs(slug) {
    boardSlug.value = slug;
    imageSlug.value = slug;
    textSlug.value = slug;
    boardForm.action = slug;
    textForm.action = slug + '/text/';
    imageForm.action = slug + '/image/';
  }


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
      console.log(response);
      if (response.data.slug) {
        var title = response.data.title + ' - Spire';
        window.history.pushState({}, title, response.data.slug);
        document.title = title;
        updateSlugs(response.data.slug);
      }
    });
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