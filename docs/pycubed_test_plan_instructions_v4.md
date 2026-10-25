# PyCubed TestStand Emulator — инструкция к текущему плану

Этот файл объясняет, как использовать `PyCubed_Test_Plan_v4.json`.

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
9. External Watchdog Recovery Test.
10. USB Data & USB Power Test.
11. ADM1176 VBATT Voltage Measurement.

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

ADM1176 VBATT voltage test, watchdog и USB уже определены. Следом логично разработать charger/battery, GPS, radio и финальную TestStand sequence.


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

## ADM1176 VBATT Voltage Measurement

Для VBATT оставляем две точки:

- **7.4 V** — nominal project operating point для 2S Li-Ion.
- **8.4 V** — верхняя точка полностью заряженной 2S батареи / charger float-voltage condition.

На каждой точке fixture выставляет VBATT, затем независимый DMM/DAQ измеряет фактическое напряжение. ADM1176 измеряет то же напряжение своим ADC.

PASS/FAIL сравнивает **ADM1176 measured voltage** с **actual fixture DMM/DAQ voltage**, а не только с setpoint источника.

Временный project/simulation limit: **±5%** на каждой из двух точек.

Логируем:
- target fixture voltage;
- actual fixture voltage;
- ADM1176 ADC code;
- calculated ADM1176 voltage;
- absolute error in volts;
- error percent;
- PASS/FAIL.

Этот ±5% limit не является официальным PyCubed manufacturing limit. Финальный production limit должен учитывать поведение ADM1176 в реальном диапазоне платы и uncertainty fixture/DMM.


## ADM1176 Overcurrent Protection / Auto-Retry

Для этого теста фиксируем:

- VBATT: **7.4 V**
- Normal load: **0.5 A**
- Overload request: **1.2 A**

При R8 = 0.1 Ω nominal current-limit level получается около **1.0 A**. Поэтому 1.2 A выбран как явный overload point.

Проверяем:

1. При 0.5 A плата работает стабильно, protection не срабатывает.
2. Fixture запрашивает нагрузку 1.2 A.
3. ADM1176 должен перейти в current-limit/protection behavior и не позволить устойчивый ток 1.2 A.
4. При сохраняющемся overload protected output должен отключиться.
5. Для варианта ADM1176-1 должен появиться automatic retry.
6. Убираем overload и возвращаем нормальную нагрузку.
7. Проверяем восстановление питания, 3.3 V rail и связи с DUT.

Точный TIMER timing пока не используем как PASS/FAIL criterion. Его можно логировать как diagnostic information и позже добавить отдельные timing limits после проверки реальной fixture и компонентов.

Этот тест проверяет protection/recovery behavior и не заменяет ADM1176 current-measurement accuracy test.
