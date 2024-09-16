from l7nh import L7NH

def main():
    # 컨트롤러 객체 생성, 이더캣 마스터 시작
    l7nh = L7NH()
    l7nh.set_position_limit([-50000000, 0])
    l7nh.open('\\Device\\NPF_{F18362F0-35E4-4793-927A-CC07A5553EDB}')  # 이더넷 어댑터 ID 입력

    # 목표 위치 -50000000, 프로파일 속도 12800000, 프로파일 가속 25600000, 프로파일 감속 6400000 으로 이동 요청
    command_number = l7nh.move_position_profile(-50000000, 12800000, 25600000, 6400000)
    
    # 모션 완료시까지 반복하여 현재 위치, 목표 위치 도착 여부 확인
    while True:
        status_command_number, current_position, reached = l7nh.get_status()
        if status_command_number == command_number and reached:
            break

    # 목표 위치 0, 프로파일 속도 12800000, 프로파일 가속 25600000, 프로파일 감속 6400000 으로 이동 요청
    command_number = l7nh.move_position_profile(0, 12800000, 25600000, 6400000)

    # 모션 완료시까지 반복하여 현재 위치, 목표 위치 도착 여부 확인
    while True:
        status_command_number, current_position, reached = l7nh.get_status()
        if status_command_number == command_number and reached:
            break

    # 이더캣 마스터 종료
    l7nh.close()


if __name__ == '__main__':
    main()
