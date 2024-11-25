token = "1871611757:AAEaBOwnGpP5j4_LHQvrSey0bYl29_EAwAs"

import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import db
from models import *
from threading import Thread
import time
import asyncio


# URL base
BASE_URL = "http://ncprac.com/api"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

threads=[]

db.session.query(db.Thread).delete()
db.session.commit()

async def start_notifying_routes(user:User, user_id:str, application:ApplicationBuilder):
    while True:
        routes = user.routes()
        if len(routes) == 0:
            screens = db.session.query(db.Screen).filter(db.Screen.user_id == user_id, db.Screen.name.like("%new_route%")).all()
            for screen in screens:
                try:
                    await application.bot.delete_message(chat_id=user_id, message_id=screen.message_id)
                except:
                    pass
                db.session.delete(screen)
            db.session.commit()
        for route in routes:
            screen = db.session.query(db.Screen).filter_by(user_id=user_id, name=f"new_route/{route.id}").first()
            if screen:
                try:
                    await application.bot.delete_message(chat_id=user_id, message_id=screen.message_id)
                except:
                    pass
                db.session.delete(screen)
                db.session.commit()
            #keyboard with button "Aceptar"
            keyboard = [[InlineKeyboardButton("Aceptar", callback_data=f'/route/start={route.id}')]]
            message = await application.bot.send_message(chat_id=user_id, text=str(route), reply_markup=InlineKeyboardMarkup(keyboard))
            screen = db.Screen(name=f"new_route/{route.id}", user_id=user_id, chat_id=user_id, message_id=message.message_id)
            db.session.add(screen)
            db.session.commit()
        await asyncio.sleep(10)

def start_notifying_routes_thread(application:ApplicationBuilder):
    loop = asyncio.get_event_loop()
    async def background_task():
        for token in db.session.query(db.Token).all():
            user = User(str(token.token))
            await start_notifying_routes(user, token.user_id, application)
    loop.create_task(background_task())





async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #get token where user_id = update.effective_chat.id, if not exist ask for login
    login_token = db.session.query(db.Token).filter_by(user_id=update.effective_chat.id).first()
    screen = db.session.query(db.Screen).filter_by(user_id=update.effective_chat.id, name="menu").first()
    if login_token is None:
        if screen:
            await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=screen.message_id, text="-")
            db.session.delete(screen)
        message = await context.bot.send_message(chat_id=update.effective_chat.id, text="No estas logueado")
        screen = db.Screen(name="menu", user_id=update.effective_chat.id, chat_id=update.effective_chat.id, message_id=message.message_id)
        db.session.add(screen)
        db.session.commit()
    else:
        if screen:
            await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=screen.message_id, text="-")
            db.session.delete(screen)
        user = User(str(login_token.token))
        #inline keyboard with options: Estoy disponible, No estoy disponible
        keyboard = [[InlineKeyboardButton("Estoy disponible", callback_data='/user/availability=True')] if not user.availability() else [InlineKeyboardButton("No estoy disponible", callback_data='/user/availability=False')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Hola {user.name}, bienvenido a NCPRAC\n{'Estas disponible' if user.availability() else 'No estas disponible'}", reply_markup=reply_markup)
        screen = db.Screen(name="menu", user_id=update.effective_chat.id, chat_id=update.effective_chat.id, message_id=message.message_id)
        db.session.add(screen)
        db.session.commit()



async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    login_token = db.session.query(db.Token).filter_by(user_id=update.effective_chat.id).first()
    if login_token is None:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="No estas logueado")
    else:
        user = User(str(login_token.token))
        query_data = query.data
        if query_data.startswith('/user/availability='):
            availability_status = query_data.split('=')[1]
            user.availability(availability_status.lower() == 'true')

            screen = db.session.query(db.Screen).filter_by(user_id=update.effective_chat.id, name="menu").first()
            if screen:
                keyboard = [[InlineKeyboardButton("Estoy disponible", callback_data='/user/availability=True')] if not user.availability() else [InlineKeyboardButton("No estoy disponible", callback_data='/user/availability=False')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=screen.message_id, text=f"Hola {user.name}, bienvenido a NCPRAC\n{'Estas disponible' if user.availability() else 'No estas disponible'}", reply_markup=reply_markup)
            else:
                keyboard = [
                    [InlineKeyboardButton("Estoy disponible", callback_data='/user/availability=True')],
                    [InlineKeyboardButton("No estoy disponible", callback_data='/user/availability=False')],
                    [InlineKeyboardButton("Aceptar Ruta", callback_data='/route/accept')]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                message = await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Hola {user.name}, bienvenido a NCPRAC\n{'Estas disponible' if user.availability() else 'No estas disponible'}", reply_markup=reply_markup)
                screen = db.Screen(name="menu", user_id=update.effective_chat.id, chat_id=update.effective_chat.id, message_id=message.message_id)
                db.session.add(screen)
                db.session.commit()
        elif query_data.startswith('/route/start='):
            user.start_route(query_data.split('=')[1])
            if login_token.route_id:
                screens = db.session.query(db.Screen).filter(db.Screen.user_id == update.effective_chat.id, db.Screen.name.like("route/%")).all()
                for screen in screens:
                    try:
                        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=screen.message_id)
                    except:
                        pass
                    db.session.delete(screen)
                db.session.commit()
            login_token.route_id = query_data.split('=')[1]
            db.session.commit()
            screens = db.session.query(db.Screen).filter(db.Screen.user_id == update.effective_chat.id, db.Screen.name.like("%new_route%")).all()
            for screen in screens:
                try:
                    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=screen.message_id)
                except:
                    pass
                db.session.delete(screen)
            db.session.commit()
            route = user.get_route(login_token.route_id)
            keyboard=[]
            if not route.pickup_time:
                keyboard.append([InlineKeyboardButton("Informar recogida", callback_data='/route/pickup')])
            if not route.end_time:
                keyboard.append([InlineKeyboardButton("Finalizar", callback_data='/route/end')])

            message = await context.bot.send_message(chat_id=update.effective_chat.id, text="***Ruta en curso***\n"+str(route), reply_markup=InlineKeyboardMarkup(keyboard))
            screen = db.Screen(name=f"route/{login_token.route_id}", user_id=update.effective_chat.id, chat_id=update.effective_chat.id, message_id=message.message_id)
            db.session.add(screen)
            db.session.commit()
        elif query_data.startswith('/route/pickup'):
            user = User(str(login_token.token))
            route = user.get_route(login_token.route_id)
            if route.pickup_time:
                await context.bot.answer_callback_query(callback_query_id=query.id, text="Ya has informado la recogida")
            else:
                user.inform_pickup(login_token.route_id)
                route = user.get_route(login_token.route_id)
                keyboard=[]
                if not route.end_time:
                    keyboard.append([InlineKeyboardButton("Finalizar", callback_data='/route/end')])
                await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=query.message.message_id, text="***Ruta en curso***\n"+str(route), reply_markup=InlineKeyboardMarkup(keyboard))
        elif query_data.startswith('/route/end'):
            user = User(str(login_token.token))
            route = user.get_route(login_token.route_id)
            if route.end_time:
                await context.bot.answer_callback_query(callback_query_id=query.id, text="Ya has finalizado la ruta")
            else:
                user.end_route(login_token.route_id)
                route = user.get_route(login_token.route_id)
                keyboard=[]
                await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=query.message.message_id, text="***Ruta finalizada***\n"+str(route), reply_markup=InlineKeyboardMarkup(keyboard))
                screens = db.session.query(db.Screen).filter(db.Screen.user_id == update.effective_chat.id, db.Screen.name.like("route/%")).all()
                for screen in screens:
                    try:
                        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=screen.message_id)
                    except:
                        pass
                    db.session.delete(screen)
                db.session.commit()
                login_token.route_id = None
                db.session.commit()

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    login_token = db.session.query(db.Token).filter_by(user_id=update.effective_chat.id).first()
    if login_token is None:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="No estas logueado")
    else:
        user = User(str(login_token.token))
        if login_token.route_id:
            route = user.get_route(login_token.route_id)
            if not route.end_time:
                if update.edited_message:
                    user.send_location(login_token.route_id, update.edited_message.location.latitude, update.edited_message.location.longitude)
                else:
                    user.send_location(login_token.route_id, update.message.location.latitude, update.message.location.longitude)

if __name__ == '__main__':
    application = ApplicationBuilder().token(token).build()
    start_notifying_routes_thread(application)
    start_handler = CommandHandler('start', start)
    #inline keyboard handler
    buttons_handler = CallbackQueryHandler(handle_buttons)
    #location_handler = MessageHandler(Filters.location, handle_location)
    location_handler = MessageHandler(filters.LOCATION, handle_location)
    application.add_handler(location_handler)
    application.add_handler(start_handler)
    application.add_handler(buttons_handler)
    
    application.run_polling()