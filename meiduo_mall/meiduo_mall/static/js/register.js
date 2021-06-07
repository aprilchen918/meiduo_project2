// We use ES6 syntax
// Create Vue object vm
let vm = new Vue({
    el: '#app',  // Get binding HTML content by ID selector
    delimiters: ['[[', ']]'],
    data: { // data object
        // v-model
        username: '',
        password: '',
        password2: '',
        mobile: '',
        allow: '',
        image_code_url: '',
        uuid:'',
        image_code: '',
        sms_code:'',
        sms_code_tip: '获取短信验证码',
        send_flag: false,   // Label whether user is waiting for enter sms code

        // v-show
        error_name: false,
        error_password: false,
        error_password2: false,
        error_mobile: false,
        error_allow: false,
        error_image_code: false,
        error_sms_code: false,

        // error_message
        error_name_message: '',
        error_mobile_message: '',
        error_image_code_message: '',
        error_sms_code_message:'',
    },
    mounted(){ // called after loading page
        // The method to generate image verify code: encapsulation idea to achieve code reuse
        this.generate_image_code()
    },
    methods: { // Define and implement event methods.
        // Send sms code
        send_sms_code(){
            // Avoid malicious users frequently click on the tag to obtain sms code
            if (this.send_flag == true) { // If user is waiting for entering sms code, reject clicking get sms code
                return;
            }
            this.send_flag = true;  // Label the user is waiting for entering sms code
            //Check mobile and image code
            this.check_mobile();
            this.check_image_code();
            if (this.error_mobile == true || this.error_image_code == true) {
                this.send_flag = false;
                return;
            }
            // Send axios request
            let url = '/sms_codes/' + this.mobile + '/?image_code=' + this.image_code + '&uuid=' + this.uuid;
            axios.get(url, {
                responseType: 'json'
            })
                .then(response => {
                    if (response.data.code == '0') {
                        // Sent sms code successfully
                        // Show Countdown 60 seconds
                        let num = 60;
                        let t = setInterval(() => {
                            if (num == 1){ // Countdown will be end
                                clearInterval(t); // Stop callback function
                                this.sms_code_tip = '获取短信验证码'; // Restore sms_code_tip prompt text
                                this.generate_image_code(); // Generate new image code
                                this.send_flag = false;
                            } else {
                                num -= 1;
                                this.sms_code_tip = num + '秒';
                            }
                        }, 1000)   // setInterval('callback function', 'time tag'
                    } else {
                        if (response.data.code = '4001') { // image code error
                            this.error_image_code_message = response.data.errmsg;
                            this.error_image_code = true;
                        } else { // 4002 sms code error
                            this.error_sms_code_message = response.data.errmsg;
                            this.error_sms_code = true;
                        }
                        this.send_flag = false;
                    }
                })
                .catch(error => {
                    console.log(error.response);
                    this.send_flag = false;
                })
            // Countdown 60 seconds
        },


        // Generate image code
        generate_image_code(){
            this.uuid = generateUUID();
            this.image_code_url = '/image_codes/' + this.uuid + '/';
        },

        // Verify username
        check_username(){
            // Username contains 5-20 characters, [a-zA-Z0-9_-]
            let re = /^[a-zA-Z0-9_-]{5,20}$/;
            if (re.test(this.username)) {
                // Match successfully, don't show error message
                this.error_name = false;
            } else {
                // Otherwise, show error message
                this.error_name_message = '请输入5-20个字符的用户名';
                this.error_name = true;
            }

            // Check whether username registered repeatedly
            if (this.error_name == false) { // Only check when username user entered is valid
                let url = '/usernames/' + this.username + '/count/';
                axios.get(url, {
                    responseType: 'json'
                })
                    .then(response => {
                        if (response.data.count == 1) {
                            // The user is already exist
                            this.error_name_message = '用户名已存在';
                            this.error_name = true;
                        } else {
                            // The user is not exist
                            this.error_name = false;
                        }
                    })
                    .catch(error => {
                        console.log(error.response);
                    })
            }
        },
        // Verify password
        check_password(){
            let re = /^[0-9A-Za-z]{8,20}$/;
            if (re.test(this.password)) {
                this.error_password = false;
            } else {
                this.error_password = true;
            }
        },
        // Verify password2
        check_password2(){
            if (this.password != this.password2) {
                this.error_password2 = true;
            } else {
                this.error_password2 = false;
            }
        },
        // Verify phone number
        check_mobile(){
            re = /^\d{10}$/;
            if (re.test(this.mobile)) {
                this.error_mobile = false;
            } else {
                this.error_mobile_message = '您输入的手机号格式不正确';
                this.error_mobile = true;
            }

            if (this.error_mobile == false) {
                let url = '/mobile/' + this.mobile + '/count/';
                axios.get(url, {
                    responseType: 'json'
                })
                    .then(response => {
                        if (response.data.count == 1) {
                            this.error_mobile_message = '手机号已存在';
                            this.error_mobile = true;
                        } else {
                            this.error_mobile = false;
                        }
                    })
                    .catch(error => {
                        console.log(error.response);
                    })
            }
        },
        // Check image code
        check_image_code(){
            if (this.image_code.length != 4) {
                this.error_image_code_message = '请填写图片验证码';
                this.error_image_code = true;
            } else {
                this.error_image_code = false;
            }
        },
        // Check sms code
        check_sms_code(){
            if (this.sms_code.length != 6) {
                this.error_sms_code_message = '请填写短信验证码';
                this.error_sms_code = true;
            } else {
                this.error_sms_code = false;
            }
        },

        // Verify whether check the agreement
        check_allow(){
            if (!this.allow){
                this.error_allow = true;
            } else {
                this.error_allow = false;
            }
        },
        // Listen table submitting event
        on_submit(){
            this.check_username();
            this.check_password();
            this.check_password2();
            this.check_mobile();
            this.check_sms_code();
            this.check_allow();

            if(this.error_name || this.error_password == true || this.error_password2 == true || this.error_mobile == true || this.error_sms_code == true || this.error_allow == true) {
                // Disable submission of the form
                window.event.returnValue = false;
            }
        },
    },
})