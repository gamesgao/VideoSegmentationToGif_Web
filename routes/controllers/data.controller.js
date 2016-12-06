var express = require('express');
var formidable = require('formidable');
var fs = require('fs');
var cp = require('child_process');
var crypto = require('crypto');
var router = express.Router();

router.get('/', data);
router.post('/uploadVideo', uploadVideo);
router.post('/checkAnalyse', checkAnalyse)

var videoTempPath = "videoTemp/";
var resultpath = "result/";

function data(req, res, next) {
    res.render('data', { title: 'VideoSegmentation' })
}

function uploadVideo(req, res, next) {
    var form = new formidable.IncomingForm();
    form.uploadDir = videoTempPath;
    form.parse(req, function(error, fields, files) {
        var ms = new Date().getTime();
        var videoMD5 = md5(String(ms + Math.random()));
        fs.renameSync(files.videoFile.path, '${videoTempPath}${videoMD5}.mp4');
        res.send(videoMD5);
    })
}

function checkAnalyse(req, res, next) {
    return res.send(-1);
}

/**
 * 计算给定值的 md5 值
 * @param  {string} text 给定值
 * @return {string}      md5
 */
function md5(text) {
    return crypto.createHash('md5').update(text).digest('hex');
};

module.exports = router;
