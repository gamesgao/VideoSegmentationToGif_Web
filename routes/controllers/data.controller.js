var express = require('express');
var formidable = require('formidable');
var fs = require('fs');
var cp = require('child_process');
var crypto = require('crypto');
var router = express.Router();

router.get('/', data);
router.post('/uploadVideo', uploadVideo);
router.post('/checkAnalyse', checkAnalyse);
router.post('/getMask', getMask);

var videoTempPath = "./videoTemp/";
var resultpath = "./public/images/result/";
var childProcessFlag = 0;
var child;

function data(req, res, next) {
    res.render('data', { title: 'VideoSegmentation' })
}

function uploadVideo(req, res, next) {
    var form = new formidable.IncomingForm();
    form.uploadDir = videoTempPath;
    form.parse(req, function(error, fields, files) {
        var ms = new Date().getTime();
        var videoMD5 = md5(String(ms + Math.random()));
        fs.renameSync(files.videoFile.path, `${videoTempPath}${videoMD5}.mp4`);
        res.send(videoMD5);
        childProcessFlag = 1;
        child = cp.exec(`python start.py ${videoMD5}.mp4`, function(error, stdout, stderr) {
            if (error) {
                childProcessFlag = -1;
                console.log(error.stack);
                console.log('Error code: ' + error.code);
            }
            childProcessFlag = 0;
            console.log('Child Process STDOUT: ' + stdout);
        })
        child.stdout.on('data', function(data) {
            console.log(data == '409');
            console.log(data == '409\n');
            console.log(data == '409\r\n');
            console.log(data.trim() == '409');
            if (data.trim() == '409') {
                childProcessFlag = 2;
            } else {
                console.log(data);
            }
        })
    })
}

function checkAnalyse(req, res, next) {
    var videoMD5 = req.body.videoMD5;
    return res.send(childProcessFlag.toString());
}

function getMask(req, res, next) {
    var mask = req.body.mask;
    childProcessFlag = 3;
    // console.log(mask.length);
    // console.log(mask[0].length);
    // for (var i = mask.length - 1; i >= 0; i--) {
    //     for (var j = mask[i].length - 1; j >= 0; j--) {
    //         if (mask[i][j] == 1) console.log(`(${i}.${j})`);
    //     }
    // }
    // fs.writeFile('1.txt', JSON.stringify(mask));
    child.stdin.write(JSON.stringify(mask));
    child.stdin.end();
    res.send("HA");
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
