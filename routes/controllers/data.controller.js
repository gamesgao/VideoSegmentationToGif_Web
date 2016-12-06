var express = require('express');
var router = express.Router();

router.get('/', data);
router.get('/requireData', reData);

function data(req, res, next) {
    res.render('data', { title: 'VideoSegmentation' })
}

function reData(req, res, next) {

}

module.exports = router;
