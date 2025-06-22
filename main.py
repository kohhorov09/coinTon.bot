from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, ReplyKeyboardMarkup
from telegram.constants import ChatMemberStatus
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler
import logging

# 🔐 TOKEN va ADMIN ID
BOT_TOKEN = "8145474409:AAG_DCe3s3eP8PI2jaJHXZ2CRMVQCZuxwzY"
ADMIN_ID = 7114973309

# 📊 Ma'lumotlar
user_db = set()
left_users = set()
required_channels = []

# 🔍 Logging
logging.basicConfig(level=logging.INFO)

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    user_db.add(user_id)

    not_subscribed = []
    for ch in required_channels:
        try:
            member = await context.bot.get_chat_member(chat_id=ch, user_id=user_id)
            if member.status not in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                not_subscribed.append(ch)
        except:
            not_subscribed.append(ch)

    if not_subscribed:
        buttons = [
            [InlineKeyboardButton(f"📢 {ch}", url=f"https://t.me/{ch.lstrip('@')}")]
            for ch in required_channels
        ]
        buttons.append([InlineKeyboardButton("✅ Tekshirish", callback_data="check_subs")])
        reply_markup = InlineKeyboardMarkup(buttons)
        await update.message.reply_text("❗ O‘yinni boshlashdan oldin quyidagi kanallarga obuna bo‘ling:", reply_markup=reply_markup)
        return

    game_button = InlineKeyboardButton("🎮 Join Game", web_app=WebAppInfo(url="https://coin-ton.vercel.app/"))
    await update.message.reply_text("✅ Obuna tasdiqlandi. O‘yinni boshlang!", reply_markup=InlineKeyboardMarkup([[game_button]]))

# /admin komandasi
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ Bu bo‘lim faqat admin uchun.")
        return

    keyboard = ReplyKeyboardMarkup([
        ["📊 Statistika", "📋 Ro‘yxat"],
        ["➕ Obuna qo‘shish", "➖ Obunani o‘chirish"],
        ["⬅️ Ortga"]
    ], resize_keyboard=True)

    await update.message.reply_text("🔧 Admin menyusi:", reply_markup=keyboard)

# Admin text handler
async def handle_admin_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text.strip()

    if user.id != ADMIN_ID:
        return

    if text == "➕ Obuna qo‘shish":
        await update.message.reply_text("📩 Kanal userni yuboring (masalan: @kanal):")
        context.user_data["adding_channel"] = True
        return

    if text == "➖ Obunani o‘chirish":
        if not required_channels:
            await update.message.reply_text("📭 Hech qanday kanal mavjud emas.")
            return
        buttons = [
            [InlineKeyboardButton(f"❌ {ch}", callback_data=f"remove_{i}")]
            for i, ch in enumerate(required_channels)
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await update.message.reply_text("O‘chirmoqchi bo‘lgan kanalni tanlang:", reply_markup=reply_markup)
        return

    if text == "📋 Ro‘yxat":
        msg = "\n".join(required_channels) if required_channels else "📭 Kanal ro‘yxati bo‘sh."
        await update.message.reply_text(msg)
        return

    if text == "📊 Statistika":
        await update.message.reply_text(f"👥 Umumiy foydalanuvchilar: {len(user_db)}\n🚪 Botdan chiqqanlar: {len(left_users)}")
        return

    if text == "⬅️ Ortga":
        await start(update, context)
        return

    if context.user_data.get("adding_channel"):
        if text.startswith("@"):
            required_channels.append(text)
            await update.message.reply_text(f"✅ Qo‘shildi: {text}")
        else:
            await update.message.reply_text("❌ Format noto‘g‘ri. @ bilan yozing.")
        context.user_data["adding_channel"] = False

# Callback handler
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data.startswith("remove_") and user_id == ADMIN_ID:
        index = int(query.data.replace("remove_", ""))
        if 0 <= index < len(required_channels):
            removed = required_channels.pop(index)
            await query.edit_message_text(f"❌ Kanal o‘chirildi: {removed}")
        else:
            await query.edit_message_text("🚫 Xatolik yuz berdi.")
        return

    if query.data == "check_subs":
        not_subscribed = []
        for ch in required_channels:
            try:
                member = await context.bot.get_chat_member(chat_id=ch, user_id=user_id)
                if member.status not in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                    not_subscribed.append(ch)
            except:
                not_subscribed.append(ch)

        if not_subscribed:
            buttons = [
                [InlineKeyboardButton(f"📢 {ch}", url=f"https://t.me/{ch.lstrip('@')}")]
                for ch in not_subscribed
            ]
            buttons.append([InlineKeyboardButton("✅ Qayta tekshirish", callback_data="check_subs")])
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.edit_message_text("🚫 Siz hali ham barcha kanallarga obuna bo‘lmagansiz:", reply_markup=reply_markup)
        else:
            game_button = InlineKeyboardButton("🎮 Join Game", web_app=WebAppInfo(url="https://coin-ton.vercel.app/"))
            await query.edit_message_text("✅ Obuna tekshirildi. O‘yinga kirishingiz mumkin!", reply_markup=InlineKeyboardMarkup([[game_button]]))

# RUN
if __name__ == "__main__":
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(MessageHandler(filters.TEXT & filters.User(ADMIN_ID), handle_admin_text))
    app.add_handler(CallbackQueryHandler(handle_callback))
    print("🤖 Bot ishga tushdi!")
    app.run_polling()
