from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from database.simple_db import db, UserRole
from utils.states import RegistrationStates
from keyboards.auth_keyboards import get_phone_keyboard, get_role_keyboard

router = Router()

