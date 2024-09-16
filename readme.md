# LS L7NH 서보 드라이브 제어 패키지

## 셋업(Windows)

- npcap 설치: https://npcap.com (설치 시 'Install Npcap in WinPcap API-compatible Mode' 선택)
- 필요 패키지 설치:
```shell
pip install pysoem
```
- 이더넷 어댑터 ID 알아내기:
```python
print(pysoem.find_adapters())
```

## 예제

```python
from l7nh import L7NH
import time


def main():
    # 컨트롤러 객체 생성, 이더캣 마스터 시작
    l7nh = L7NH()
    l7nh.open('\\Device\\NPF_{F18362F0-35E4-4793-927A-CC07A5553EDB}')  # 이더넷 어댑터 ID 입력
    time.sleep(1)  # 초기화 시간 주기

    # 목표 위치 0, 프로파일 속도 12800000, 프로파일 가속 25600000, 프로파일 감속 25600000 으로 이동 요청
    l7nh.move_position_profile(0, 12800000, 25600000, 25600000)
    time.sleep(0.1)

    # 모션 완료시까지 반복하여 현재 위치, 목표 위치 도착 여부 확인
    while True:
        current_position, reached = l7nh.get_status(0.1)
        if reached:
            break
    # 목표 위치 -5000000, 프로파일 속도 12800000, 프로파일 가속 25600000, 프로파일 감속 25600000 으로 이동 요청
    l7nh.move_position_profile(-5000000, 12800000, 25600000, 25600000)
    time.sleep(0.1)

    # 모션 완료시까지 반복하여 현재 위치, 목표 위치 도착 여부 확인
    while True:
        current_position, reached = l7nh.get_status(0.1)
        if reached:
            break

    # 이더캣 마스터 종료
    l7nh.close()


if __name__ == '__main__':
    main()

```