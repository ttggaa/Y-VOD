// common.js

// dayjs
dayjs.locale('zh-cn');
dayjs.extend(dayjs_plugin_relativeTime);

// sidebar
$(document).ready(function () {
    $('.ui.sidebar').sidebar('attach events', '.toc.item');
});

// popup timestamp
$('.popup-timestamp').attr({
    'data-tooltip': function () {
        return dayjs($(this).attr('data-timestamp')).format('YYYY-M-D H:mm:ss');
    },
    'data-position': 'top left',
    'data-inverted': ''
}).text(function () {
    return dayjs($(this).attr('data-timestamp')).fromNow();
});
