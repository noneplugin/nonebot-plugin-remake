from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    remake_send_forword_msg: bool = False
