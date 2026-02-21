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
    stage2_gate = State()
    stage2_intro = State()

    # ===== Предпросмотр =====
    preview = State()

    # ===== Редактирование =====
    edit_field = State()      # выбор поля для редактирования
    edit_photo = State()      # выбор фото для редактирования
    edit_value = State()      # ввод нового значения поля

    # ===== Админ =====
    admin_reject_reason = State()
    admin_send_model_message = State()
    admin_request_info_message = State()
    admin_create_post = State()
    admin_edit_post_text = State()
    admin_edit_post_photo = State()
