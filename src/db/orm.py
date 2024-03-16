"""ORM operation with sqlalchemy
"""
from typing import List, Dict, Any

from sqlalchemy.orm import DeclarativeBase, Session
from sqlalchemy.exc import SQLAlchemyError

from src.bot.message import send_message


def insert_data(session: Session,
                table: DeclarativeBase, 
                list_dict_data: List[Dict[str, Any]]) -> None:
    
    obj_list = []

    try: 

        for record in list_dict_data:
            data_obj = table(**record)
            obj_list.append(data_obj)

        session.add_all(obj_list)
        session.commit()
    except SQLAlchemyError as e:

        send_message(f"""SQL database 問題: \n
                        Error Message: {str(e)}
                        """)
        session.rollback()


        


