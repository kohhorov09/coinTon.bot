from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, ReplyKeyboardMarkup
from telegram.constants import ChatMemberStatus
from telegram.ext import (
    Application, CommandHandler, ContextTypes,
    MessageHandler, filters, CallbackQueryHandler
)
import logging

BOT_TOKEN = "8145474409:AAG_DCe3s3eP8PI2jaJHXZ2CRMVQCZuxwzY"  # ← o‘zingizning tokeningizni yozing
ADMIN_ID = 7114973309

user_db = set()
left_users = set()
required_channels = []

logging.basicConfig(level=logging.INFO)

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_db.add(user_id)

    not_subscribed = []
    for ch in required_channels:
        try:
            member = await context.bot.get_chat_member(ch, user_id)
            if member.status not in [
                ChatMemberStatus.MEMBER,
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.OWNER,
            ]:
                not_subscribed.append(ch)
        except:
            not_subscribed.append(ch)

    if not_subscribed:
        buttons = [
            [InlineKeyboardButton(f"📢 {ch}", url=f"https://t.me/{ch.lstrip('@')}")]
            for ch in not_subscribed
        ]
        buttons.append([InlineKeyboardButton("✅ Tekshirish", callback_data="check_subs")])
        markup = InlineKeyboardMarkup(buttons)
        await update.message.reply_text("❗ Obuna bo‘ling:", reply_markup=markup)
    else:
        button = InlineKeyboardButton("🎮 Join Game", web_app=WebAppInfo(url="https://coin-ton.vercel.app/"))
        await update.message.reply_text("✅ Obuna bo‘ldingiz!", reply_markup=InlineKeyboardMarkup([[button]]))

# /admin komandasi
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    keyboard = ReplyKeyboardMarkup([
        ["📊 Statistika", "📋 Ro‘yxat"],
        ["➕ Obuna qo‘shish", "➖ Obunani o‘chirish"],
        ["⬅️ Ortga"]
    ], resize_keyboard=True)
    await update.message.reply_text("🔧 Admin menyusi:", reply_markup=keyboard)

# Admin matn
async def handle_admin_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    text = update.message.text

    if text == "📊 Statistika":
        await update.message.reply_text(f"👥 Foydalanuvchilar: {len(user_db)}\n🚪 Chiqqanlar: {len(left_users)}")

# Callback
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == "check_subs":
        not_subscribed = []
        for ch in required_channels:
            try:
                member = await context.bot.get_chat_member(ch, user_id)
                if member.status not in [
                    ChatMemberStatus.MEMBER,
                    ChatMemberStatus.ADMINISTRATOR,
                    ChatMemberStatus.OWNER,
                ]:
                    not_subscribed.append(ch)
            except:
                not_subscribed.append(ch)

        if not_subscribed:
            buttons = [
                [InlineKeyboardButton(f"📢 {ch}", url=f"https://t.me/{ch.lstrip('@')}")]
                for ch in not_subscribed
            ]
            buttons.append([InlineKeyboardButton("✅ Qayta tekshirish", callback_data="check_subs")])
            markup = InlineKeyboardMarkup(buttons)
            await query.edit_message_text("🚫 Obuna to‘liq emas:", reply_markup=markup)
        else:
            button = InlineKeyboardButton("🎮 Join Game", web_app=WebAppInfo(url="https://coin-ton.vercel.app/"))
            await query.edit_message_text("✅ Obuna tasdiqlandi!", reply_markup=InlineKeyboardMarkup([[button]]))

# Run
if __name__ == "__main__":
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(MessageHandler(filters.TEXT & filters.User(ADMIN_ID), handle_admin_text))
    app.add_handler(CallbackQueryHandler(handle_callback))

    print("🤖 Bot ishga tushdi!")
    app.run_polling()
