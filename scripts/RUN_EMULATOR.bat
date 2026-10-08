@echo off
cd /d %~dp0\..
python -c "from emulator import pycubed_emulator as e; e.initialize_emulator(); print('Serial:', e.get_serial_number()); print('Station:', e.get_station_id()); print('Power:', e.power_on()); print('3V3:', e.read_3v3()); print('Boot:', e.test_boot()); print('IMU:', e.test_imu()); print('Battery:', e.read_battery()); e.cleanup()"
pause
