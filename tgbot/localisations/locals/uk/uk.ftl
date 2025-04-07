wrong_input = ❗️Схоже ви щось не те ввели.
keyboard-back = ⬅️Назад

start_link-already_printer = Ви вже друкар, вам не треба підтверджувати це ще раз.
start_link-client_to_printer = Ваш статус було змінено з клієнта до прінтера. Ласкаво просимо.
start_link-printer_to_client = Не думаю що ми підтримуємо зміну статусу з друкаря до клієнта.
    Вибачте.
invite_activated = Новий друкар тільки що доєднався до команди через інвайт!: @{$username}
wrong_invite = Вибачте, це запрошення не дійсне.

start = Вітаємо у MetaPrint.

    Ваш статус: {$type}
client = клієнт
printer = друкар
start_keyboard-client_orders = 🗂Ваші замовлення
start_keyboard-make_order = 📝Створити нове замовлення
start_keyboard-printer_orders = 🗂Ваші прийняті замовлення
start_keyboard-info = 📄Інформація
start_keyboard-settings = ⚙️Налаштування
start_keyboard-admin_panel = 🤖Адмінська панель

info = Тут купа важливої інформації. Прям КУПА.
settings = Тут опції для вас.
admin_panel = Адмінська панель для кращого адміна!

settings_keyboard-change_language = 🇺🇦/🇬🇧/🇺🇸Змінити мову

admin_panel_keyboard-clear_local_database = Очистити локальну базу бота
admin_panel_keyboard-show_users = Показати користувачів
admin_panel_keyboard-change_usermode = Змінити користувацький режим
admin_panel_keyboard-create_invite = Створити нове запрошення

clear_local_database = УВАГА!
    ВИ ЗБИРАЄТЕСЯ ОЧИСТИТИ ЛОКАЛЬНУ БАЗУ ДАНИХ БОТА!
    ЦЕ ЗАЧЕПИТЬ ЛИШЕ ЛОКАЛЬНУ БАЗУ ДАНИХ БОТА З ІНФОРМАЦІЄЮ ПРО КОРИСТУВАЧІВ, А НЕ ОСНОВНУ БАЗУ ДАНИХ, АЛЕ ВСЕ ОДНО ДУМАЙТЕ ДВІЧІ!
    ВВЕДІТЬ "clearLocalDatabase1234" ЩОБ ЗРОБИТИ ЦЕ.

database_cleared = <i>З видаленням цієї локальної бази даних нить вашої долі обривається.
    Завантажте бекап щоб відновити течію долі, або живіть далі у проклятому світі який самі й створили.</i>

change_usermode = Змініть ваш тип юзера на правах адміна.

    Нинішній режим: {$type}

order_posted = Ваше замовлення #{$order_id} було опубліковано.

callback_chat_order-accept = Прийняти
callback_chat_order-cancel = Відмінити
callback-order_acceptance_confirmation = Ви впевнені що хочете прийняти це замовлення?
callback-chat_order_accepted-printer = Чудово, ви тільки що прийняли замовлення #{$order}!
    Спеціальний модерований чат було створено для вас з клієнтом: {$link}
callback-chat_order_accepted-client = Ваше замовлення #{$order} тілько що було прийнято друкарем {$printer_usertag}!
    Новий модерований чат було створено для вас: {$link}
callback-chat_order_cancelled = Ваш вибір було відмінено, ніхто ні про що не дізнається.
callback-chat_order_already_was_accepted = Вибачте, це замовлення вже було зайняте кимось іншим поки ви намагалися взяти його собі.

chat_title = Чат metaprint {$client_name} з {$printer_name}
chat_description = Чат замовлення #{$order_id}

client_orders_list = Список ваших замовлень.
    Сторінка #{$page}
printer_orders_list = Список замовлень що ви прийняли.
    Сторінка #{$page}
order_list-page_back = ⬅️
order_list-page_forward = ➡️

text_template_base = <b>Замовлення:</b> #{$order}
    <b>Замовник:</b> {$first_name} {$last_name}
    <b>Місто:</b> {$city}

    <b>Продукти:</b>
    {$orders}
    <b>Поточний друкар:</b> {$printer}
    <b>Статус:</b> {$status}

    text_template_order = <b>Продукт</b> #{$product_number}
    <b>Назва:</b> {$name}
    <b>Ціна:</b> {$price} грн
    <b>Кількість:</b> {$quantity}
    <b>Вартість:</b> {$cost} грн
    <b>Опис:</b> {$description}

menuButtonWebApp = Нове замовлення

please_send_file = Будь ласка, надішліть файл для цього замовлення в одному з цих форматів:
    <code>.stl, .3mf, .obj, .rar, .zip, .7z</code>
err_no_file = Те що ви зараз надіслали - не файл. І цей бот очікує файл.
err_wrong_file = Не вірний формат файлу.
    Будь ласка, виберіть один з цих форматів: <code>.stl, .3mf, .obj, .rar, .zip, .7z</code>
file_processed = Файл прийнято, ви можете повернутися у інтерфейс створення замовлення.

    🔽
file_processed_but_cant_connect = Файл прийнято, але не можемо зв'язатися з вашою формою.
file_cancelled = Ви відмінили завантаження файлу з інтерфейсу.