document.addEventListener('DOMContentLoaded', function() {

  // Forms
  var textForm = document.getElementById('text-form');
  var imageForm = document.getElementById('image-form');
  var boardForm = document.getElementById('board-form');
  var deleteImageForm = document.getElementById('delete-image-form');
  var deleteColorForm = document.getElementById('delete-color-form');

  // Inputs
  var filenameInput = document.getElementById('image-filename');
  var textInput = document.getElementById('text-text');
  var boardTitle = document.getElementById('board-title');
  var deleteImageId = document.getElementById('delete-image-id');
  var deleteColorId = document.getElementById('delete-color-id');

  // Slugs
  var boardSlug = document.getElementById('board-slug');
  var imageSlug = document.getElementById('image-slug');
  var textSlug = document.getElementById('text-slug');

  var images = document.getElementById('images');
  var colors = document.getElementById('colors');
  var overlay = document.getElementById('overlay');
  var dropzone = document.getElementById('dropzone');

  var showOverlay = false;
  var dragTimeout = -1;
  var i;
  var boardInputs = boardForm.getElementsByTagName('input');
  var autoSaveTimeoutId;

  function imageTemplate(image) {
    return '<div class="image" data-id="' + image.id + '">' +
    '<img src="' + image.url + '">' +
    '<a class="delete-image" href="#">X</a>' +
    '</div>';
  }

  function colorTemplate(color) {
    return '<div class="color" style="background-color: #' + color.hex + '" data-id="' + color.id + '">' +
    '<p>#' + color.hex + '</p>' +
    '<a class="delete-color" href="#">X</a>' +
    '</div>';
  }

  function validImageUrl(url) {
    var pattern = /^http[s]?:\/\/[a-zA-Z0-9\.\-\/]+\.(jpeg|jpg|gif|png|svg)$/;
    return pattern.test(url);
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
      success: functions.success || function() { /* noop */ },

      error: functions.error || function(response) { console.log(response); },

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

    xhr.open('POST', url);
    xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');

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
      case 'image/svg+xml':
        extention = '.svg';
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

  function attemptToCreateImagePlaceholder(url) {
    if (!validImageUrl(url)) {
      console.log(url, ' is not a URL.');
      return;
    }

    images.insertAdjacentHTML('beforeend', imageTemplate({
      url: url,
      id: -1,
    }));

    return images.lastChild;
  }

  function submitText(text) {
    textInput.value = text;
    previewElement = attemptToCreateImagePlaceholder(text);
    submitFormAjax(textForm, {
      success: function(response) {
        textInput.value = '';

        if (response.data.image && previewElement) {
          previewElement.dataset.id = response.data.image.id;
          registerDeleteImageButton(previewElement.querySelector('.delete-image'));
        } else if (response.data.color) {
          colors.insertAdjacentHTML('beforeend', colorTemplate(response.data.color));
          registerDeleteColorButton(colors.lastChild.querySelector('.delete-color'));
        }

      },

      error: function(response) {
        console.log(response.error.data);
      },

    });
  }

  function showDropzone() {
    dropzone.className += ' active';
  }

  function hideDropzone() {
    dropzone.className = dropzone.className.replace('active', '');
  }

  function dragLeave(e) {
    showOverlay = false;
    clearTimeout(dragTimeout);
    dragTimeout = setTimeout(function() {
      if (!showOverlay) {
        hideDropzone();
      }
    }, 200);
  }

  function dragEnter(e) {
    showDropzone();
    showOverlay = true;
  }

  function dragOver(e) {
    showOverlay = true;
    clearTimeout(dragTimeout);
  }

  function registerAutoSave(input) {
    input.addEventListener('blur', function() {
      clearTimeout(autoSaveTimeoutId);
      autoSaveTimeoutId = setTimeout(saveBoard, 500);
    });
  }

  function deleteBlock(event, idInput, deleteForm) {
    event.preventDefault();
    var block = event.target.parentNode;
    if (block.dataset.id === -1) {
      console.log('Can\'t delete.');
    }

    idInput.value = block.dataset.id;

    // Hide the block
    block.className += ' hidden';
    submitFormAjax(deleteForm, {
      success: function(response) {
        // Delete the block
        block.parentNode.removeChild(block);
      },

      error: function(response) {
        // Show the block again
        block.className = block.className.replace('hidden', '');
      },

    });
  }

  function registerDeleteImageButton(button) {
    button.addEventListener('click', function(event) {
      deleteBlock(event, deleteImageId, deleteImageForm);
    });
  }

  function registerDeleteColorButton(button) {
    button.addEventListener('click', function(event) {
      deleteBlock(event, deleteColorId, deleteColorForm);
    });
  }

  var myDropzone = new Dropzone('#dropzone', {
    url: 'https://minimill-spire.s3.amazonaws.com',
    thumbnailWidth: null,
    thumbnailHeight: null,
    maxThumbnailFilesize: 15,
    previewsContainer: '.dropzone-previews',
    previewTemplate: document.getElementById('preview-template').innerHTML,
    clickable: false,
    init: function() {
      this.on('sending', function(file, xhr, formData) {
        var filename = getFilename(file);
        file.previewElement.dataset.s3Filename = filename;
        formData.append('key', filename);
      });

      this.on('dragleave', function(e) {
        dragLeave();
      });

      this.on('drop', function(e) {
        dragLeave();
        e.dataTransfer.items[0].getAsString(function(url) {
          submitText(url);
        });
      });
    },

    success: function(file, response) {
      filenameInput.value = file.previewElement.dataset.s3Filename;
      submitFormAjax(imageForm, {
        success: function(response) {
          if (response.data.image) {
            file.previewElement.dataset.id = response.data.image.id;
            registerDeleteImageButton(file.previewElement.querySelector('.delete-image'));
          }
        },

      });
    },

  });

  document.body.addEventListener('dragenter', dragEnter);
  document.body.addEventListener('dragover', dragOver);

  textForm.addEventListener('submit', function(e) {
    e.preventDefault();
    submitText(textInput.value);
    return false;
  });

  for (i = 0; i < boardInputs.length; i++) {
    registerAutoSave(boardInputs[i]);
  }

  var deleteImageButtons = document.getElementsByClassName('delete-image');
  for (i = 0; i < deleteImageButtons.length; i++) {
    registerDeleteImageButton(deleteImageButtons[i]);
  }

  var deleteColorButtons = document.getElementsByClassName('delete-color');
  for (i = 0; i < deleteColorButtons.length; i++) {
    registerDeleteColorButton(deleteColorButtons[i]);
  }

});
