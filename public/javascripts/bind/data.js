var app = new Vue({
    el: "#selector",
    data: {
        uploadOpen: false, // 只有在文件内容更改后才允许上传文件
        fileWarning: "", // 上传文件中的警告信息
        currentState: 1, // 当前模式, 1 代表上传文件模式, 2 代表展示分析结果模式
        videoMD5: "", // 已上传的 video 文件的MD5值
        uploadTotal: 1, // 文件总大小
        uploadLoaded: 0 // 当前已上传的大小
    },
    computed: {
        progress: function() {
            return this.uploadLoaded / this.uploadTotal;
        }
    },
    methods: {
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
                    setTimeout(function() { that.checkAnalyse(that.videoMD5); }, 60000)
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
                if (res.data === "-1") {
                    console.log(1);
                    return setTimeout(function() { that.checkAnalyse(that.videoMD5); }, 60000);
                } else {
                    console.log("hahaha");
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
            if (fileName.indexOf(".bmp") === -1) {
                this.fileWarning = "上传的文件必须是 mp4 文件!";
                this.uploadOpen = false;
                return;
            }

            // 一切检查通过, 允许上传!
            this.fileWarning = "";
            this.uploadOpen = true;
        },

        reUploadFile: function() {
            this.fileWarning = "";
            this.uploadOpen = false;
            this.currentState = 1;
        }
    }
})
