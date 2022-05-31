# Прококол JIM основные ключи:
ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'
SENDER = 'from'
DESTINATION = 'to'

# Прочие ключи, используемые в протоколе
PRESENCE = 'presence'
RESPONSE = 'response'
ERROR = 'error'
MESSAGE = 'message'
MESSAGE_TEXT = 'mess_text'
EXIT = 'exit'

# Словари - ответы:

# 200
RESPONSE_200 = {RESPONSE: 200}
# 400
RESPONSE_400 = {
    RESPONSE: 400,
    ERROR: None
}
