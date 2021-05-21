from models import *
import db
import os
 
 
if __name__ == "__main__":
    path = SQLITE3_NAME
    if not os.path.isfile(path):
 
        # テーブルを作成する
        Base.metadata.create_all(db.engine)
 
    # サンプルユーザ(admin)を作成
    admin = User(username='admin', password='fastapi', mail='hoge@example.com')
    db.session.add(admin)  # 追加
    db.session.commit()  # データベースにコミット
    
    photo = Photo(username="riku", image="../rikuAngles/rikuAngle0.JPG")
    # サンプルタスク
    print(photo)
    db.session.add(photo)
    db.session.commit()
 
    db.session.close()