'use strict';

var autoprefixer = require('gulp-autoprefixer');
var browserSync = require('browser-sync').create();
var cache = require('gulp-cached');
var fs = require('fs');
var gulp = require('gulp');
var jscs = require('gulp-jscs');
var jshint = require('gulp-jshint');
var plumber = require('gulp-plumber');
var reload = browserSync.reload;
var rename = require('gulp-rename');
var sass = require('gulp-sass');
var minifyCss = require('gulp-minify-css');
var scsslint = require('gulp-scss-lint');
var sourcemaps = require('gulp-sourcemaps');
var uglify = require('gulp-uglify');
var exec = require('child_process').exec;

gulp.task('sass:lint', function() {
  gulp.src('./app/static/src/sass/*.scss')
    .pipe(plumber())
    .pipe(scsslint());
});

gulp.task('sass:build', function() {
  gulp.src('./app/static/src/sass/style.scss')
    .pipe(rename({suffix: '.min'}))
    .pipe(plumber())
    .pipe(sourcemaps.init())
    .pipe(sass({
      outputStyle: 'compressed',
    }))
    .pipe(autoprefixer())
    .pipe(sourcemaps.write())
    .pipe(gulp.dest('./app/static/dist/css/'));
});

gulp.task('sass:optimized', function() {
  gulp.src('./app/static/src/sass/style.scss')
    .pipe(rename({suffix: '.min'}))
    .pipe(plumber())
    .pipe(sass({
      outputStyle: 'compressed',
    }))
    .pipe(autoprefixer())
    .pipe(minifyCss({compatibility: 'ie8'}))
    .pipe(gulp.dest('./app/static/dist/css/'));
});

gulp.task('sass', ['sass:lint', 'sass:build']);

gulp.task('js:build', function() {
  gulp.src(['./app/static/src/js/**/*.js'])
    .pipe(plumber())
    .pipe(uglify())
    .pipe(gulp.dest('app/static/dist/js'));
});

gulp.task('js:lint', function() {
  gulp.src(['./app/static/src/js/**/*.js', '!./app/static/src/js/lib/*', 'Gulpfile.js'])
    .pipe(plumber())
      .pipe(jscs())
    .pipe(jshint())
    .pipe(jshint.reporter('default'));
});

gulp.task('js', ['js:lint', 'js:build']);

gulp.task('images', function() {
  gulp.src('./app/static/src/img/**/*')
    .pipe(plumber())
    .pipe(gulp.dest('./app/static/dist/img'));

  // gulp.src('src/favicon.ico')
  //   .pipe(plumber())
  //   .pipe(gulp.dest('./dist/'));
});

gulp.task('fonts', function() {
  gulp.src('./app/static/src/font/*')
    .pipe(plumber())
    .pipe(gulp.dest('./app/static/dist/font'));
});

gulp.task('run', function() {
  var proc = exec('./config/runserver.sh');
});

gulp.task('watch', function() {
  gulp.watch('./app/templates/**/*.html', reload);
  gulp.watch('./app/static/src/sass/**/*.scss', ['sass'], reload);
  gulp.watch('./app/static/src/img/**/*', ['images'], reload);
  gulp.watch(['./app/static/src/js/**/*.js', 'Gulpfile.js'], ['js'], reload);
});

gulp.task('build', ['sass', 'images', 'fonts', 'js']);
gulp.task('build:optimized', ['sass:optimized', 'images', 'fonts', 'js']);

// use default task to launch Browsersync and watch JS files
gulp.task('serve', ['build', 'run'], function() {

  // Serve files from the root of this project
  browserSync.init({
    notify: false,
    proxy: '127.0.0.1:5000',
  });

  // add browserSync.reload to the tasks array to make
  // all browsers reload after tasks are complete.
  gulp.start(['watch']);
});
