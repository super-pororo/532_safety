import cv2
import numpy as np
import time
from pylogix import PLC
import os

current_directory = os.path.dirname(os.path.abspath(__file__))

# 'images' 폴더 경로 만들기
images_folder = os.path.join(current_directory, 'images')

# 'images' 폴더가 없으면 생성
if not os.path.exists(images_folder):
    os.makedirs(images_folder)

temp = 0
whT = 320

confThreshold_1 = 0.5
confThreshold_2 = 0.7
nmsThreshold = 0.3

classesFile = 'coco.names'

with open(classesFile, 'rt') as f:
    classNames = f.read().split('\n')

model_config = 'yolov3.cfg'
model_weights = 'yolov3.weights'

#소형모델
#model_config = 'yolov3-tiny.cfg'
#model_weights = 'yolov3-tiny.weights'

net = cv2.dnn.readNetFromDarknet(model_config, model_weights)
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

def findObjects(outputs, img):
    global temp
    emg = False
    hT, wT, cT = img.shape
    bbox = []
    classIds = []
    confs = []

    for output in outputs:
        for det in output:
            scores = det[5:]
            classId = np.argmax(scores)
            confidence = scores[classId]
            if confidence > confThreshold_1:
                w, h = int(det[2]*wT), int(det[3]*hT)
                x, y = int((det[0]*wT) - w/2), int((det[1]*hT) - h/2)
                bbox.append([x,y,w,h])
                classIds.append(classId)
                confs.append(float(confidence))

    indices = cv2.dnn.NMSBoxes(bbox, confs, confThreshold_2, nmsThreshold)
    print(f"식별된 대상 : {len(indices)} 개")
    
    for i in indices:
        i = i
        box = bbox[i]
        x, y, w, h = box[0], box[1], box[2], box[3]
        cv2.rectangle(img, (x,y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(img, f"{classNames[classIds[i]].upper()} {int(confs[i]*100)}%",
                    (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
    if len(indices) != 0:
        print(classNames[classIds[indices[0]]])
        if classNames[classIds[indices[0]]] == "person":
            print("사람이 감지되었습니다.")
            
            # 파일 이름 설정
            file_name = f'img{temp}.jpeg'
            
            # 전체 파일 경로 생성
            file_path = os.path.join(images_folder, file_name)

            cv2.imwrite(file_path, img)
            temp = temp+1
            emg = True
            return emg
        emg = False
        return emg
     
def show(img):       
    blob = cv2.dnn.blobFromImage(img, 1/255, (whT, whT), [0,0,0], True, crop=False)
    net.setInput(blob)
    layerNames = net.getLayerNames()        
    a = net.getUnconnectedOutLayers()
    outputNames = [layerNames[i - 1] for i in net.getUnconnectedOutLayers()]
    outputs = net.forward(outputNames)        
    emg = False
    emg = findObjects(outputs, img)
    if emg == True:
        return img, True
    else: return img, False
