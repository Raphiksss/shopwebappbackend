## shopyaebal

# что б потом реализовать профиль иницализируешь сайт как веб апп и достаешь tg_id:
const tg = window.Telegram.WebApp;
tg.expand();
const user = tg.initDataUnsafe.user;
и далтше по обычному гет запросу уже данные получаешь
кто прочтет - лох
