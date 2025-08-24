import sys
import cv2
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox
from ui import Ui_MainWindow
from pylogix import PLC

import FindObject
print("hi")
with open('setting.txt', 'r') as file:
    PLC_IP     = file.readline().strip()  # 첫 번째 줄 (plcip)
    HEART_TAG  = file.readline().strip()  # 두 번째 줄 (HEART TAG)
    EMG_TAG    = file.readline().strip()  # 세 번째 줄 (EMG TAG)
    HEART2_TAG = file.readline().strip()  # 네 번째 줄 (HEART2 TAG, 공정으로 신호전송)
    setting_top_left_x     = file.readline().strip()
    setting_top_left_y     = file.readline().strip()
    setting_bottom_right_x = file.readline().strip()
    setting_bottom_right_y = file.readline().strip()
    
print(PLC_IP,"\n", HEART_TAG,"\n", EMG_TAG) 


class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        self.text_plcip.setText(str(PLC_IP))
        self.text_heartbit.setText(str(HEART_TAG))
        self.text_emgbit.setText(str(EMG_TAG))

        # 타이머 설정 (300ms마다 업데이트)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.timeout.connect(self.check_plc_signal)
        self.timer.start(300)  # 300ms 주기로 프레임 업데이트

        # 웹캠 설정
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) # 윈도우 전용
        #self.cap = cv2.VideoCapture(0,cv2.CAP_AVFOUNDATION) # 맥 전용

        # 파일에서 읽어온 변수 객체화
        self.setting_top_left_x     = setting_top_left_x    
        self.setting_top_left_y     = setting_top_left_y    
        self.setting_bottom_right_x = setting_bottom_right_x
        self.setting_bottom_right_y = setting_bottom_right_y

        # 파일에서 읽어온 변수 GUI에 입력
        self.PLC_IP     = PLC_IP
        self.HEART_TAG  = HEART_TAG 
        self.EMG_TAG    = EMG_TAG   
        self.HEART2_TAG = HEART2_TAG
        
        self.lineEdit_Top_Left_X.setText(str(setting_top_left_x))
        self.lineEdit_Top_Left_Y.setText(str(setting_top_left_y))
        self.lineEdit_Bottom_Right_X.setText(str(setting_bottom_right_x))
        self.lineEdit_Bottom_Right_Y.setText(str(setting_bottom_right_y))

        # apply 버튼클릭 버튼 연결
        self.pushButton_Apply.clicked.connect(self.pushButton_Apply_click)

    def check_number(self, target):
        try:
            if target.isdigit() and (len(target) != 0):
                target = int(target)
            else:
                QMessageBox.information(self, '입력값 오류', '입력된 값이 숫자가 아니거나 아무것도 입력되지 않았습니다.')
                return False
            if (target < 3001) and (target > 0):
                return True
            else: 
                QMessageBox.information(self, '입력값 오류', '숫자 0 ~ 3000까지 입력해 주세요.')
                return False
        except Exception as e:
            print("check_number 오류",e)


    def input_ok(self):
        # 버튼 입력 안했을경우
        inputs = {
        "Top_Left_X": self.lineEdit_Top_Left_X.text(),
        "Top_Left_Y": self.lineEdit_Top_Left_Y.text(),
        "Bottom_Right_X": self.lineEdit_Bottom_Right_X.text(),
        "Bottom_Right_Y": self.lineEdit_Bottom_Right_Y.text()
        }

        for label, value in inputs.items():
            if not self.check_number(value):
                print(f"{label} 입력 오류")
                return False
            print(f"{label} 정상입력")
        return True

    def pushButton_Apply_click(self):
        if self.input_ok() == True:
            self.setting_top_left_x     = self.lineEdit_Top_Left_X.text()    
            self.setting_top_left_y     = self.lineEdit_Top_Left_Y.text()    
            self.setting_bottom_right_x = self.lineEdit_Bottom_Right_X.text()
            self.setting_bottom_right_y = self.lineEdit_Bottom_Right_Y.text()
            print("매개변수 정상입력 완료")
        else: print("매개변수 오류")

        with open('setting.txt', 'w') as file:
            file.write(self.PLC_IP + '\n')
            file.write(self.HEART_TAG + '\n')
            file.write(self.EMG_TAG + '\n')
            file.write(self.HEART2_TAG + '\n')

            file.write(self.setting_top_left_x + '\n')
            file.write(self.setting_top_left_y+ '\n')
            file.write(self.setting_bottom_right_x + '\n')
            file.write(self.setting_bottom_right_y+ '\n')

    def check_plc_signal(self):
        ###############################
        with PLC() as comm:
            comm.IPAddress = PLC_IP
            ret = comm.Read(HEART_TAG)
            #print(ret.TagName, ret.Value, ret.Status)
        ###############################
        if ret.Value == True:
            self.label_HEARTBIT.setStyleSheet("background-color: green; color: white; font-size: 12px;")
            #print("HEART BIT True")
        else:
            self.label_HEARTBIT.setStyleSheet("background-color: white; color: black; font-size: 12px;")
            #print("HEART BIT False")
            
    def bit_on_emg(self):
        with PLC() as comm:
            comm.IPAddress = PLC_IP
            ret = comm.Write(EMG_TAG, True)
            print(ret.TagName, ret.Value, ret.Status)
            self.label_EMERGENCY.setStyleSheet("background-color: red; color: white; font-size: 12px;")
        
    def bit_off_emg(self):
        # ###############################
        with PLC() as comm:
            comm.IPAddress = PLC_IP
            ret = comm.Write(EMG_TAG, False)
            #print(ret.TagName, ret.Value, ret.Status)
        
        with PLC() as comm:
            comm.IPAddress = PLC_IP
            ret = comm.Read(HEART2_TAG)
            if ret.Value == True:
                ret = comm.Write(HEART2_TAG, False)
                self.label_HEARTBIT_2.setStyleSheet("background-color: white; color: black; font-size: 12px;")    
            else:
                ret = comm.Write(HEART2_TAG, True)
                self.label_HEARTBIT_2.setStyleSheet("background-color: green; color: white; font-size: 12px;")
        # ###############################
        self.label_EMERGENCY.setStyleSheet("background-color: white; color: black; font-size: 12px;")

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            # 특정 영역을 자르기 위해 픽셀 값을 지정
            top_left_x = int(self.setting_top_left_x) # 450
            top_left_y = int(self.setting_top_left_y) # 100
            bottom_right_x = int(self.setting_bottom_right_x) # 800
            bottom_right_y = int(self.setting_bottom_right_y) # 450
            
            # 지정한 픽셀 범위로 이미지 자르기
            cropped_frame = frame[top_left_y:bottom_right_y, top_left_x:bottom_right_x]
            
            cropped_frame, emg = FindObject.show(cropped_frame)

            if emg == True:
                self.bit_on_emg()
            elif emg == False:
                self.bit_off_emg()
             
            # 이미지를 PyQt에서 사용할 수 있는 QImage로 변환
            cropped_height, cropped_width, channel = cropped_frame.shape
            bytes_per_line = 3 * cropped_width
            q_img = QtGui.QImage(cropped_frame.data.tobytes(), cropped_width, cropped_height, bytes_per_line, QtGui.QImage.Format_RGB888).rgbSwapped()

            # QLabel에 이미지 설정
            self.label.setPixmap(QtGui.QPixmap.fromImage(q_img))

    def closeEvent(self, event):
        # 창을 닫을 때 비상신호 해제합니다.
        self.bit_off_emg()
        # 창을 닫을 때 웹캠을 해제합니다.
        self.cap.release()
        event.accept()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
