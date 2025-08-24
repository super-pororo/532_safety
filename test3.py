import cv2
import numpy as np
import time

temp = 0
device = 0
cap = cv2.VideoCapture(device)
whT = 320
PLC_IP = "10.72.23.108"
TAG = "B532[10].0"

window_name = 'YOLOv3'

while True:
    # 프레임 읽기
    ret, frame = cap.read()

    # 프레임 읽기 실패 시 종료
    if not ret:
        print("Error: Could not read frame.")
        break

    # 화면에 프레임 보여주기
    cv2.imshow("Camera Feed", frame)

    # 'q' 키를 누르면 루프 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 카메라 장치와 창 닫기
cap.release()
cv2.destroyAllWindows()

print("여기 바꿈")