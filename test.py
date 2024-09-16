from l7nh import L7NH


def main():
    l7nh = L7NH()
    l7nh.set_position_limit([-50000000, 0])
    l7nh.open('\\Device\\NPF_{F18362F0-35E4-4793-927A-CC07A5553EDB}')

    command_number = l7nh.move_position_profile(
        target_position=-50000000, profile_velocity=12800000,
        profile_acceleration=25600000, profile_deceleration=6400000)

    while True:
        status_command_number, current_position, reached = l7nh.get_status()
        if status_command_number == command_number and reached:
            break

    command_number = l7nh.move_position_profile(
        target_position=0, profile_velocity=12800000,
        profile_acceleration=25600000, profile_deceleration=6400000)

    while True:
        status_command_number, current_position, reached = l7nh.get_status()
        if status_command_number == command_number and reached:
            break

    l7nh.close()


if __name__ == '__main__':
    main()
