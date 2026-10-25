# PyCubed TestStand Emulator — инструкция к текущему плану

Этот файл объясняет, как использовать `pycubed_test_plan_v1.json`.

## Что уже зафиксировано

Оператор сканирует badge/ID перед каждой платой. ID предыдущего оператора не подставляется автоматически. Смена оператора не требует новой Golden Reference verification.

Golden Reference действительна только в той же boot-session станции и не более 12 часов. После reboot или по истечении 12 часов следующий DUT требует новую verification. Если есть подозрение на станцию или что-то заменили, согласованное правило — сделать reboot.

## Текущий порядок DUT tests

1. Safe Power-Up / Overcurrent.
2. 3.3 V Rail.
3. MCU Detection through SWD.
4. Internal Flash / Bootloader / Firmware Verification.
5. MRAM Read/Write.
6. microSD Provisioning/Verification.
7. BMX160 IMU Functional Test.
8. ADM1176 Multi-Point Current Test.

## Как трактовать значения

Не выдавать simulation/project values за официальные manufacturing limits.

- 7.4 V, ~30 mA и 250 mA safety limit в Safe Power-Up — примеры для эмулятора.
- 3.20–3.40 V — наш project/simulation range вокруг nominal 3.30 V.
- 125/250/500 mA для ADM1176 — тестовые точки полного тока через R8 = 0.1 Ω.
- Финальные производственные limits должны учитывать datasheet, tolerance компонентов и uncertainty fixture.

## Internal Flash

Проверяем bootloader и firmware против последней версии, предоставленной производителем и одобренной для станции. Также проверяем checksum/hash.

Если версия отсутствует или устарела — программируем approved image, затем проверяем снова.

## MRAM и microSD

MRAM: write → read → compare → clear/initialize. Не форматируем как filesystem.

microSD:
- новая плата: FAT32 format → write/read/compare → delete test file;
- retest/service: не форматировать автоматически, только non-destructive test.

## IMU

Fixture имеет Position 1 = 0° и Position 2 = 45°.

Оператор получает popup и вручную поворачивает fixture в фиксированную позицию.

Accelerometer: проверяем изменение gravity components.
Gyro: точный °/s не нужен; проверяем stationary → motion on expected axis → stationary.
Magnetometer: communication/data-validity check.

## ADM1176 current test

Целевые TOTAL currents через R8:

- 125 mA → 12.5 mV
- 250 mA → 25.0 mV
- 500 mA → 50.0 mV

Electronic load регулируется до тех пор, пока независимый измеритель fixture не покажет целевой общий ток.

Сравниваем ADM1176 не с setpoint нагрузки, а с actual fixture measurement.

Например, если сама плата берёт около 30 mA, для 250 mA total дополнительная нагрузка будет примерно 220 mA, но финальная точка определяется именно измеренным total current.

## Watchdog

External watchdog test is now defined. The MAX706R-family watchdog timeout is 1.00–2.25 s, with 1.6 s typical. TestStand stops the watchdog heartbeat, measures the time to reset, then confirms that the DUT reboots and communication returns. The ~200 ms reset delay is a separate supervisory timing value and is logged only as a reference.

## Logging

Каждый DUT run создаёт отдельный JSON:

`test_data/<SERIAL>_<STATION>_<YYYYMMDD>_<HHMMSS>_<MICROSECONDS>.json`

Сохраняются operator ID, station ID, serial number, verification status, все шаги, значения, limits, attempts и итоговый PASS/FAIL.

## Cleanup

Cleanup выполняется всегда:
1. Power OFF DUT.
2. Electronic load → safe state.
3. Reset/release emulator resources.
4. Save result JSON.

## Источники

Ссылки сохранены внутри JSON в разделе `sources`.

Основные:
- PyCubed v0.5 schematic
- ADM1176 datasheet
- TPS54226 datasheet
- ATSAMD51J19A documentation
- MR25H40 documentation
- CircuitPython PyCubed v0.5 page

## Что ещё не закончено

Следом логично разработать ADM1176 VBATT voltage test, затем watchdog, USB, charger/battery, GPS, radio и финальную TestStand sequence.


## USB Data & USB Power Test

USB is split into two separate subtests.

### A. USB Data Communication
- DUT remains powered from fixture VBATT.
- USB is used for data.
- Verify enumeration, expected device/interface, TEST_PING / TEST_PONG, and byte-for-byte data transfer.
- One reconnect/re-enumeration retry is allowed for a transient issue.

### B. USB Power Operation
- Turn fixture VBATT OFF.
- Enable the PyCubed USB power path.
- Connect USB-C.
- Verify that the board powers from USB.
- Verify the 3.3 V rail.
- Verify USB enumeration and communication again.

USB board power and USB battery charging are different functions. Charging will be tested later in the battery/charger block.

The physical fixture must control power paths so that unintended back-powering between VBATT and USB is avoided.