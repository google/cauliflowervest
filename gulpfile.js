var gulp = require('gulp'),
  del = require('del'),
  shell = require('shelljs'),
  path = require('path'),
  fs = require('fs'),
  vulcanize = require('gulp-vulcanize'),
  rename = require("gulp-rename");

gulp.task('clean', function() {
  del.sync(['tmp/**']);
});

/**
 * Prepare app for vulcanization.
 * Copy all webcomponents into tmp/app and place each of them in separate
 * directory.
 */
gulp.task('copy', ['clean'], function() {
  gulp.src('src/cauliflowervest/server/static/index.html')
      .pipe(gulp.dest("tmp/app"));

  gulp.src('src/cauliflowervest/server/frontend/*')
      .pipe(rename(function (path) {
        path.dirname += '/' + path.basename;
      })).pipe(gulp.dest("tmp/app"));

  return gulp.src('bower_components/**').pipe(gulp.dest('tmp/app'));
});

/**
 * Everything placed inside app.html.
 * Including js(not compiled), except google-closure-library.
 */
gulp.task('vulcanize', ['copy'], function() {
  return gulp.src('tmp/app/index.html').pipe(vulcanize({
    excludes: [],
    inlineScripts: true,
    inlineCss: true,
    stripExcludes: false,
    excludes: [
      '/static/goog/base.js'
    ],
  })).pipe(rename('app.html'))
      .pipe(gulp.dest('tmp'));
});
