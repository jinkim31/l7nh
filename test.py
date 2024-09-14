from l7nh import L7NH
import time


def main():
    l7nh = L7NH()
    l7nh.open('\\Device\\NPF_{F18362F0-35E4-4793-927A-CC07A5553EDB}')  # 이더넷 어댑터 ID 입력
    time.sleep(1)  # 초기화 시간 주기

    for _ in range(3):
        l7nh.move_to_position(0)  # 위치 0으로 이동 요청
        time.sleep(0.1)
        while True:
            current_position, reached = l7nh.get_status(0.1)
            if reached:
                break

        l7nh.move_to_position(-1000000)
        time.sleep(0.1)
        while True:
            current_position, reached = l7nh.get_status(0.1)
            if reached:
                break
    l7nh.close()


if __name__ == '__main__':
    main()
