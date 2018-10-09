// common.js

// sidebar
$(document).ready(function () {
    $('.ui.sidebar').sidebar('attach events', '.toc.item');
});

// footer copyright
$('#copyright').html(function () {
    return '<i class="copyright outline icon"></i> 2011-' +  new Date().getFullYear() + ' 北京云英一语教育咨询有限公司 版权所有';
});
