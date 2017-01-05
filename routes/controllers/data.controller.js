var express = require('express');
var formidable = require('formidable');
var fs = require('fs');
var cp = require('child_process');
var crypto = require('crypto');
var router = express.Router();

router.get('/', data);
router.post('/uploadFile', uploadFile);
router.post('/checkAnalyse', checkAnalyse);
router.post('/getMask', getMask);

var videoTempPath = "./videoTemp/";
var resultpath = "./public/images/result/";
var childProcessFlag = 0;
var child;
var isG = 0; // the switch to change the python way 0 or C way 1

function data(req, res, next) {
    res.render('data', { title: 'Video Segmentation By G&C' })
}

function uploadFile(req, res, next) {
    var form = new formidable.IncomingForm();
    form.uploadDir = videoTempPath;
    form.parse(req, function(error, fields, files) {
        //将文件名以.分隔，取得数组最后一项作为文件后缀名。
        var types = files.file.name.split('.');
        var type = types[types.length - 1];
        var ms = new Date().getTime();
        console.log(fields.selection);
        if (fields.selection == 0) var videoMD5 = md5(String(ms + Math.random()));
        else var videoMD5 = fields.videoMD5;
        if (fields.selection == 0) fs.renameSync(files.file.path, `${videoTempPath}${videoMD5}.${type}`);
        else fs.renameSync(files.file.path, `${videoTempPath}${videoMD5}.bg`);
        res.send(videoMD5);
        if (fields.selection == 0) {
            childProcessFlag = 1;
            if(isG == 1) calSegmentByGoogle(videoMD5, type, isG);
            else generateGIF(videoMD5, type, isG);
        }
    })
}

function calSegmentByGoogle(videoMD5, type, isGoogle){
    child1 = cp.exec(`../../seg_tree_sample --input_file=${videoTempPath}${videoMD5}.${type} --logging --write_to_file`, function(error, stdout, stderr){
        if (error) {
            childProcessFlag = -1;
            console.log(error.stack);
            console.log('Error code: ' + error.code);
        }
        // childProcessFlag = 0;
        console.log('Child Process STDOUT: ' + stdout);
        renderSegmentVideo(videoMD5, type, isGoogle);
    });
    child1.stdout.on('data', function(data) {
            console.log(data);
    });
}

function renderSegmentVideo(videoMD5, type, isGoogle){
    child2 = cp.exec(`../../segment_renderer --input_file=${videoTempPath}${videoMD5}.${type}.pb --output_image_dir=temp --logging`, function(error, stdout, stderr){
        if (error) {
            childProcessFlag = -1;
            console.log(error.stack);
            console.log('Error code: ' + error.code);
        }
        // childProcessFlag = 0;
        console.log('Child Process STDOUT: ' + stdout);
        generateGIF(videoMD5, type, isGoogle);
    });
    child2.stdout.on('data', function(data) {
            console.log(data);
    });
}

function generateGIF(videoMD5, type, isGoogle){
    console.log(`python start.py ${videoMD5}.${type} ${isGoogle}`);
    child = cp.exec(`python start.py ${videoMD5}.${type} ${isGoogle}`, function(error, stdout, stderr) {
        if (error) {
            childProcessFlag = -1;
            console.log(error.stack);
            console.log('Error code: ' + error.code);
        }
        childProcessFlag = 0;
        console.log('Child Process STDOUT: ' + stdout);
    })
    child.stdout.on('data', function(data) {
        console.log(data.trim() == (videoMD5 + '.' + type));
        if (data.trim() == (videoMD5 + '.' + type)) {
            childProcessFlag = 2;
        } else {
            console.log(data);
        }
    })
}


function checkAnalyse(req, res, next) {
    var videoMD5 = req.body.videoMD5;
    return res.send(childProcessFlag.toString());
}


function getMask(req, res, next) {
    var mask = req.body.mask;
    childProcessFlag = 3;
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
