from aiogram.fsm.state import State, StatesGroup


class ApplicationStates(StatesGroup):
    # ===== Анкета =====
    name = State()
    city = State()
    phone = State()
    age = State()
    living = State()
    devices = State()
    device_model = State()
    work_time = State()
    headphones = State()
    telegram = State()
    experience = State()
    photo_face = State()
    photo_full = State()

    # ===== Предпросмотр =====
    preview = State()

    # ===== Редактирование =====
    edit_field = State()      # редактирование текстовых полей
    edit_photo = State()  
    edit_value = State()    # редактирование фото

    # ===== Админ =====
    admin_reject_reason = State()
    admin_create_post = State()
