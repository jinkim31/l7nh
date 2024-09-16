# LS L7NH 서보 드라이브 제어 패키지

## 셋업(Windows)

- npcap 설치: https://npcap.com (설치 시 'Install Npcap in WinPcap API-compatible Mode' 선택)
- 필요 패키지 설치:
```shell
pip install pysoem
```
- 이더넷 어댑터 ID 알아내기:
```python
import pysoem
print(pysoem.find_adapters())
```

## 예제
⚠️ 휴먼랩 리니어스테이지 기준 carriage를 모터 쪽 끝에 가깝게 이동시킨 상태에서 전원 인가 후 아래 코드 실행 시 좌우 끝까지 빠르게 이동함. 
안전한 구동을 위해 `target_position`과 `profile_velocity`를 줄여서 테스트할 것을 권장함.
```python
from l7nh import L7NH


def main():
    l7nh = L7NH()
    l7nh.set_position_limit([-50000000, 0])
    l7nh.open('\\Device\\NPF_{F18362F0-35E4-4793-927A-CC07A5553EDB}')

    command_number = l7nh.move_position_profile(
        target_position=-50000000, profile_velocity=12800000,
        profile_acceleration=25600000, profile_deceleration=6400000)

    while True:
        status_command_number, target_reached, current_position = l7nh.get_status()
        print(f'current position: {current_position}')
        if status_command_number == command_number and target_reached:
            break

    command_number = l7nh.move_position_profile(
        target_position=0, profile_velocity=12800000,
        profile_acceleration=25600000, profile_deceleration=6400000)

    while True:
        status_command_number, target_reached, current_position = l7nh.get_status()
        print(f'current position: {current_position}')
        if status_command_number == command_number and target_reached:
            break

    l7nh.close()


if __name__ == '__main__':
    main()

```