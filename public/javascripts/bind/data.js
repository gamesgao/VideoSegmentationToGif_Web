var canvas;
var context;
var resultpath = "/images/result/";
var timeIntervalForCheck = 5000;


var app = new Vue({
    el: "#selector",
    data: {
        uploadOpen: false, // 只有在文件内容更改后才允许上传文件
        fileWarning: "", // 上传文件中的警告信息
        currentState: 1, // 当前模式, 1 代表上传文件模式, 2 代表展示分析结果模式
        videoMD5: "", // 已上传的 video 文件的MD5值
        uploadTotal: 1, // 文件总大小
        uploadLoaded: 0, // 当前已上传的大小
        uploadMaskOpen: false, //mask的上传按钮
        gifShow: false, //gif图片是否已经显示
        gifPath: "" //gif文件路径
    },
    computed: {
        progress: function() {
            return this.uploadLoaded / this.uploadTotal;
        }
    },
    methods: {
        chooseFile: function() {
            $('#videoFile')[0].click();
        },
        uploadFile: function() {
            var file = document.getElementById("videoFile").files[0];

            // 禁止重复上传
            this.fileWarning = "正在上传文件中...请稍后...";
            this.uploadOpen = false;

            // 构建新的 FormData
            var fileFormData = new FormData();
            fileFormData.append("videoFile", file);
            fileFormData.append("videoFileName", file.name);

            var that = this;
            this.$http.post('/data/uploadVideo', fileFormData, {
                progress: function(event) {
                    console.log(event.total);
                    that.uploadTotal = event.total;
                    that.uploadLoaded = event.loaded;
                }
            }).then(function(res) {
                if (res.data.length === 32) {
                    this.videoMD5 = res.data;
                    this.fileWarning = "正在分析文件中...请稍后...";
                    setTimeout(function() { that.checkAnalyse(that.videoMD5); }, timeIntervalForCheck)
                } else {
                    alert(res.data);
                }
            }, function(err) {
                console.log(err);
            })

        },

        checkAnalyse: function(videoMD5) {

            var that = this;

            this.$http.post('/data/checkAnalyse', { videoMD5: videoMD5 }).then(function(res) {

                // 如果返回的数据是 -1, 就说明还没有分析完
                if (res.data === "1" || res.data === "3") {
                    console.log("not end!");
                    return setTimeout(function() { that.checkAnalyse(that.videoMD5); }, timeIntervalForCheck);
                } else if (res.data === "-1") {
                    console.log("the python wrong error");
                } else if (res.data === "2") {
                    that.fileWarning = "显示第一帧图像";
                    that.currentState = 2;
                    that.uploadMaskOpen = true;
                    canvas = $('#interact');
                    context = document.getElementById('interact').getContext('2d');
                    bindEvent();
                    var img = $(new Image());
                    img.attr("src", resultpath + `${videoMD5}.mp4.jpg`);
                    img.load(function() {
                        canvas.attr("width", img.get(0).width);
                        canvas.attr("height", img.get(0).height);
                        context.drawImage(img.get(0), 0, 0);
                        context.strokeStyle = "#000000";
                        context.lineJoin = "round";
                        context.lineWidth = 2;
                    })
                } else {
                    this.gifPath = resultpath + `${videoMD5}.mp4.gif`;
                    this.gifShow = true;
                    console.log("the process is end!");
                }
            }, function(err) {
                console.log(err);
            })
        },

        checkFileName: function() {
            try {
                var fileName = document.getElementById("videoFile").files[0].name;
            } catch (err) {
                console.log("读取文件信息错误:" + err);
                return;
            }


            // 检查是否为 video 文件
            if (fileName.indexOf(".mp4") === -1) {
                this.fileWarning = "上传的文件必须是 mp4 文件!";
                this.uploadOpen = false;
                return;
            }

            // 一切检查通过, 允许上传!
            this.fileWarning = "";
            this.uploadOpen = true;
        },

        uploadMask: function() {
            var that = this;
            this.uploadMaskOpen = false;
            var mask = new Array();
            for (var i = 0; i < parseInt(canvas.attr("height")); i++) {
                mask[i] = new Array();
                for (var j = 0; j < parseInt(canvas.attr("width")); j++) {
                    mask[i][j] = 0;
                }
            }
            var data = context.getImageData(0, 0, parseInt(canvas.attr("width")), parseInt(canvas.attr("height"))).data;
            for (var i = 0; i < data.length; i += 4) {
                if (data[i] == 0 && data[i + 1] == 0 && data[i + 2] == 0) {
                    mask[parseInt((i / 4) / parseInt(canvas.attr("width")))][(i / 4) % parseInt(canvas.attr("width"))] = 1;
                }
            }

            this.$http.post('/data/getMask', { mask: mask }).then(function(res) {
                setTimeout(function() { that.checkAnalyse(that.videoMD5); }, timeIntervalForCheck);
            })
        }
    }
})


function bindEvent() {
    var paint = false;

    canvas.mousedown(function(e) {
        if (app.currentState == 2) {
            context.save();
            var mouseX = e.pageX - this.offsetLeft;
            var mouseY = e.pageY - this.offsetTop;
            context.beginPath();
            context.moveTo(mouseX, mouseY);
            context.stroke();
            paint = true;
            context.restore();
        }
    });

    canvas.mousemove(function(e) {
        if (app.currentState == 2) {
            if (paint) { //是不是按下了鼠标
                var mouseX = e.pageX - this.offsetLeft;
                var mouseY = e.pageY - this.offsetTop;
                context.lineTo(mouseX, mouseY);
                context.stroke();
            }
        }
    });

    canvas.mouseup(function(e) {
        if (app.currentState == 2) {
            paint = false;
        }
    });

    canvas.mouseleave(function(e) {
        if (app.currentState == 2) {
            paint = false;
        }
    });
}
