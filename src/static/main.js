/*
webpackでファイルをバンドルファイルを出力するファイル
*/

// CSSファイル

// Bootstrapのスタイルシート側の機能を読み込む
import "bootstrap/dist/css/bootstrap.min.css";
// BootstrapToggleのスタイルシート側の機能を読み込む
// import "bootstrap4-toggle/css/bootstrap4-toggle.css";

import '../static/accounts/css/sb-admin.css';
// import '../static/storage/css/sb-admin.css';

import 'datatables.net-dt';
// import 'datatables.net-dt/css/jquery.dataTables.min.css';

import 'datatables.net-colreorder-dt';
import 'datatables.net-colreorder-dt/css/colReorder.dataTables.min.css';

import 'datatables.net-select-dt';
import 'datatables.net-select-dt/css/select.dataTables.min.css';

import 'datatables.net-bs4';
import 'datatables.net-bs4/css/dataTables.bootstrap4.min.css';

import 'datatables.net-autofill-bs4';
import 'datatables.net-autofill-bs4/css/autoFill.bootstrap4.min.css';

import 'jquery-colorbox/example2/colorbox.css';
// import png from 'jquery-colorbox/example2/images/control.png';

import 'dropzone/dist/dropzone.css';

import "bootstrap-datetimepicker-npm/build/css/bootstrap-datetimepicker.min.css";

import '../static/common/css/validate.css';

import '../static/accounts/css/accounts.css';

// import '../static/bulk/css/bulk.css';

// import '../static/payment/css/payment.css';

// import '../static/storage/css/storage.css';

import '../static/common/css/icon.css';

import 'slick-carousel/slick/slick.css'
import 'slick-carousel/slick/slick-theme.css'

// import '../static/task/css/task.css';

import '@fortawesome/fontawesome-free/css/solid.min.css';
import '@fortawesome/fontawesome-free/css/all.min.css';
import '@fortawesome/fontawesome-free/css/fontawesome.min.css';


import 'toastr/build/toastr.css';

// リセットなので一番下
// import '../static/common/css/reset.css';



// JavaScript用

// BootstrapのJavaScript側の機能を読み込む
import 'jquery';
import "popper.js";
import "bootstrap";
import "bootstrap4-toggle";
import 'datatables.net';
import 'datatables.net-colreorder';
import 'datatables.net-select';
import 'datatables.net-bs4';
import 'datatables.net-autofill-bs4';
import 'jquery-pwd-measure';
import 'jquery-validation';
import 'jquery-colorbox';
import 'jquery.quicksearch';
import 'moment';
import 'locale';
import 'slick-carousel';

import '@fortawesome/fontawesome-free/js/fontawesome';
import '@fortawesome/fontawesome-free/js/solid';
import '@fortawesome/fontawesome-free/js/regular';

import '../static/common/js/validate';
import '../static/accounts/js/accounts';
import '../static/accounts/js/sb-admin';
// import '../static/storage/js/storage';
// import '../static/bulk/js/bulk';
// import '../static/task/js/task';


import 'bootstrap-datetimepicker-npm';
import 'jquery-datepicker';


// import 'toastr/build/toastr.min.js';

import toastr from 'toastr'
window.toastr = toastr


window.Dropzone = require('dropzone/dist/min/dropzone.min');
