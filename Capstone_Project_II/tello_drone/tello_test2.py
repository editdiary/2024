import time
import cv2
from threading import Thread
from djitellopy import Tello


def record_video(tello, frame_read, keepRecording):
    # 동영상 저장을 위한 설정
    width, height = 960, 720        # Tello의 기본 해상도
    fps = 30                        # 프레임 속도

    # 비디오 코덱 설정 및 VideoWriter 객체 생성
    fourcc = cv2.VideoWriter_fourcc(*'MP4V')        # H.264 코덱
    video_writer = cv2.VideoWriter('tello_video.mp4', fourcc, fps, (width, height))

    try:
        while keepRecording():
            # 프레임 읽기
            frame = frame_read.frame
            if frame is not None:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                cv2.imshow("Tello Frame", frame)
                video_writer.write(frame)   # 현재 프레임을 비디오 파일에 저장
                key = cv2.waitKey(1) & 0xFF
                if key == ord('s'):         # 's' 키를 눌러 사진 저장
                    cv2.imwrite('tello_picture.png', frame)
                    print("Picture taken and saved as tello_picture.jpg")
                time.sleep(1/fps)
            else:
                print("Failed to capture frame")
    except Exception as e:
        print(f"Error in video recording: {e}")
    finally:
        # 모든 창 닫기 및 비디오 저장 종료
        cv2.destroyAllWindows()
        video_writer.release()
        print("Video recording stopped and saved")

def main():
    # Tello 객체 생성
    tello = Tello()
    keepRecording = True

    try:
        # Tello 연결 & 스트리밍 활성화
        tello.connect()
        tello.streamon()
        print("Tello connected and stream started")

        # 약간의 대기 시간 추가 (스트리밍 초기화 시간 확보)
        time.sleep(3)

        # 프레임 읽기 객체
        frame_read = tello.get_frame_read()

        # 영상 녹화
        recorder = Thread(target=record_video, args=(tello, frame_read, lambda: keepRecording))
        recorder.start()

        # 드론 조작
        tello.takeoff()         # tello 드론 이륙
        tello.move_up(70)      # 100cm 상승
        tello.rotate_counter_clockwise(360)     # 360도 회전
        tello.land()            # 착륙
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        keepRecording = False
        recorder.join()
        tello.streamoff()
        print("Tello disconnected and program ended")

if __name__ == "__main__":
    main()