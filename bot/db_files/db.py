
from discord import Message
import numpy as np

from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy.exc import IntegrityError, InterfaceError


# connect with data base
engine = create_engine('sqlite:///filestorage.sqlite', echo=False)
# manage tables 
base = declarative_base()


class File(base):
    __tablename__ = "Files"

    message_id = Column(Integer, unique = True, primary_key = True)
    channel_id = Column(Integer)
    parent_file = Column(String)
    file_index = Column(Integer)

    def __init__(self, parent_file: str, file_index: int, message_data: tuple or Message) -> None:
        self.parent_file = parent_file
        self.file_index = file_index    

        if isinstance(message_data, Message):
            self.message_id = message_data.id
            self.channel_id = message_data.channel.id

        else:
            self.message_id, self.channel_id = message_data

    # Use of __dict__ will break queries TODO double check this
    def to_dict(self) -> dict:
        return {"channel_id":self.channel_id, "message_id":self.message_id, 
                "parent_file":self.parent_file, "file_index":self.file_index}


    def __repr__(self) -> str:
        return f"<File object | parent_file:{self.parent_file}, file_index:{self.file_index}>"


def add_file(file : File or dict):
    '''
    Attempts to add a file to the database.\n
    Returns true if succesful false if not
    '''
    with Session(engine) as session:
        try:
            file = file if isinstance(file, File) else File(**file)

            session.add(file)

            session.commit()

            return True

        except IntegrityError as e:
            print(f'Invalid entry: {e}')

        except InterfaceError as e:
            print(f'Invalid param:{e}')
        
        return False


def delete_entry(parent_file):
    with Session(engine) as session:
        instances = session.query(File.parent_file).filter_by(parent_file = parent_file)

        for instance in instances:
            session.delete(instance)

        session.commit()


def get_parent_files():
    with Session(engine) as session:
        parent_files = session.query(File.parent_file).all()

    parent_files = [str(file[0]) for file in parent_files]

    parent_files = np.unique(parent_files)

    return parent_files


def get_file_entries(parent_file: str):
    with Session(engine) as session:
        entries = session.query(File).filter_by(parent_file = parent_file).all()
    
    entries = [entry.to_dict() for entry in entries]

    return entries


def clear_database():
    with Session(engine) as session:
        entries = session.query(File).all()

        for entry in entries:
            session.delete(entry)

        session.commit()


# Run this to create the database initially 
# base.metadata.create_all(engine)