import face_recognition
import pathlib
import numpy as np

path = pathlib.Path("./rikukaroes/")
names = [p for p in path.iterdir() if p.match("*.JPG")]
print(a for a in names)
# あるいは import glob で name = glob.glob("faces_me/*.jp*g")

def encoding(name): # 128次元のエンコーディング
    img = face_recognition.load_image_file(name)
    return face_recognition.face_encodings(img)

enc = np.array([encoding(name) for name in names])
print(enc)
#画像の大きさを処理する必要がある

dist = [face_recognition.face_distance(enc, e) for e in enc]
# 表示（0.5より大きければ * を付ける）
for i in range(1, len(names)):
    for j in range(i):
        print(np.array2string(dist[i][j],precision=3, separator=","), end=",")
        # if dist[i][j] > 0.5:
        #     print(f" {dist[i][j]:4.2f}*", end="")
        # else:
        #    print(f"{dist[i][j]:4.2f}", end="")
    print()