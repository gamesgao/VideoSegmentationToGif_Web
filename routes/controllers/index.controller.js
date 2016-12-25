var express = require('express');
var router = express.Router();

router.get('/', index);

function index(req, res, next) {
    res.render('index', {
        title: 'Video Segmentation By G&C',
    })
}

module.exports = router;
