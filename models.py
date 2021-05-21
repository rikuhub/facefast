from datetime import datetime
 
from db import Base
 
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.sql.functions import current_timestamp
from sqlalchemy.dialects.mysql import INTEGER, BOOLEAN
 
import hashlib
 
SQLITE3_NAME = "./db.sqlite3"
 

class User(Base):
    """
    Userテーブル
 
    id       : 主キー
    username : ユーザネーム
    password : パスワード
    mail     : メールアドレス
    """
    __tablename__ = 'user'
    id = Column(
        'id',
        INTEGER(unsigned=True),
        primary_key=True,
        autoincrement=True,
    )
    username = Column('username', String(256))
    password = Column('password', String(256))
    mail = Column('mail', String(256))
 
    def __init__(self, username, password, mail):
        self.username = username
        # パスワードはハッシュ化して保存
        self.password = hashlib.md5(password.encode()).hexdigest()
        self.mail = mail
 
    def __str__(self):
        return str(self.id) + ':' + self.username
        
 
class Photo(Base):
    """
    Photoテーブル
 
    id       : 主キー
    username : 人物
    Image    : 画像
    """
    __tablename__ = 'photo'
    id = Column(
        'id',
        INTEGER(unsigned=True),
        primary_key=True,
        autoincrement=True,
    )
    username = Column('name', String(256))
    image = Column('filepath', String(256))
 
    def __init__(self, username, image):
        self.username = username
        self.image = image
 
    def __str__(self):
        return str(self.id) + ':' + self.username