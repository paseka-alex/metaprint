wrong_input = ❗️Looks like you have a wrong input.
keyboard-back = ⬅️Back

start_link-already_printer = You are already a printer, you don't need to do it again.
start_link-client_to_printer = Your status have been changed from client to printer. Welcome.
start_link-printer_to_client = I don't think we accept change from printer to client at this moment.
    Sorry.
invite_activated = New priner just joined the command via invitation link!: @{$username}
wrong_invite = Sorry, this invitation link is invalid.

start = Welcome to the MetaPrint.

    Your status: {$type}
client = client
printer = printer
start_keyboard-client_orders = 🗂Your orders
start_keyboard-make_order = 📝Make a new order
start_keyboard-printer_orders = 🗂Your acceped orders
start_keyboard-info = 📄Info
start_keyboard-settings = ⚙️Settings
start_keyboard-admin_panel = 🤖Admin panel

info = There is a lot of useful information. A LOT.
settings = There is settings for you.
admin_panel = Admin panel for the best admin!

settings_keyboard-change_language = 🇺🇦/🇬🇧/🇺🇸Change language

admin_panel_keyboard-clear_local_database = Clear local bot database
admin_panel_keyboard-show_users = Show users
admin_panel_keyboard-change_usermode = Change usermode
admin_panel_keyboard-create_invite = Create new invite link

clear_local_database = ATTENTION!
    YOU ARE ABOUT TO CLEAR LOCAL DATABASE OF THE BOT!
    IT WILL ONLY AFFECT INFO OF THE USERS IN THE BOT AND NOT THE PRODUCTION DATABASE, BUT STILL THINK TWICE!
    TYPE "clearLocalDatabase1234" TO DO THIS.

database_cleared = <i>With this local database deletion, the thread of prophecy is severed.
    Restore a backup to restore the weave of fate, or persist in the doomed world you have created.</i>

change_usermode = Change your usermode as an admin.

    Current usermode: {$type}

order_posted = Your order #{$order_id} has been posted.

callback_chat_order-accept = Accept
callback_chat_order-cancel = Cancel
callback-order_acceptance_confirmation = Are you sure you want to accept this exact order?
callback-chat_order_accepted-printer = Good, you just accepted an order #{$order}!
    Special monitored chat with your client has been created for you and the client: {$link}
callback-chat_order_accepted-client = Your order #{$order} just has been accepted by {$printer_usertag}!
    New moderated chat has been created for you: {$link}
callback-chat_order_cancelled = Your choice has been cancelled, nobody will know.
callback-chat_order_already_was_accepted = Sorry, this order was already taken while you tried to approve it.

chat_title = Metaprint chat {$client_name} with {$printer_name}
chat_description = Chat of order #{$order_id}

client_orders_list = The list of your orders.
    Page #{$page}
printer_orders_list = The list of orders you accepted.
    Page #{$page}
order_list-page_back = ⬅️
order_list-page_forward = ➡️

text_template_base = <b>Order:</b> #{$order}
    <b>Client:</b> {$first_name} {$last_name}
    <b>City:</b> {$city}

    <b>Products:</b>
    {$orders}
    <b>Current printer:</b> {$printer}
    <b>Status:</b> {$status}

    text_template_order = <b>Product</b> #{$product_number}
    <b>Name:</b> {$name}
    <b>Price:</b> {$price} грн
    <b>Quantity:</b> {$quantity}
    <b>Cost:</b> {$cost} грн
    <b>Description:</b> {$description}

menuButtonWebApp = New order

please_send_file = Please, send a file for your order in one of those file formats:
    <code>.stl, .3mf, .obj, .rar, .zip, .7z</code>
err_no_file = Whatever you just sent - it's not a file. And the file is expected.
err_wrong_file = This is the wrong file format.
    Please, select one of these: <code>.stl, .3mf, .obj, .rar, .zip, .7z</code>
file_processed = File accepted, you can return to webapp.

    🔽
file_processed_but_cant_connect = File was accepted, but can't connect to your webapp.
file_cancelled = You cancelled file uploading from a webapp.