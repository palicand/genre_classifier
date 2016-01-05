/**
 * Created by palickaa on 04/01/16.
 */
'use strict';

var gulp = require('gulp'),
    browserify = require('gulp-browserify'),
    size = require('gulp-size'),
    clean = require('gulp-clean');
// tasks


gulp.task('transform', function () {
    return gulp.src('./server/static/scripts/jsx/main.js')
        .pipe(browserify({transform: ['reactify']}))
        .pipe(gulp.dest('./server/static/scripts/js'))
        .pipe(size());
});

gulp.task('clean', function () {
    return gulp.src(['./project/static/scripts/js'], {read: false})
        .pipe(clean());
});

gulp.task('default', function() {
    gulp.start('transform');
});

gulp.task('debug', function() {
    gulp.start('transform');
    gulp.watch('./server/static/scripts/jsx/main.js', ['transform']);
});
