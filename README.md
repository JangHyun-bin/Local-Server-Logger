# Introduction

---

This is a log management program designed for the company's local server.
The program monitors a specific directory in the background.
If certain activities are detected, the program logs them.

해당 로그 관리 프로그램은 사내 로컬 서버를 위해 제작되었습니다.
특정 경로를 상시 모니터링하며 지정된 경로의 자녀 폴더에 csv 포맷 로그 파일을 생성합니다.
파일이 수정, 삭제, 생성될 경우 각 로그에 기록됩니다.

--- 

주요 기능:

- Create a .csv log file in each immediate child folder of the specified path.
- Continuously monitor the contents under the specified path, logging any file modifications, deletions, or creations in each folder's log.
- Operate from the system tray without a GUI.

- 지정된 경로의 한단계 자녀 폴더에 .csv 로그 파일 생성
- 이후 지정된 경로 아래의 내용을 상시 모니터링하며 파일이 수정, 삭제, 생성될 경우 각 폴더의 로그에 기록합니다.
- 시스템 트레이에서 동작 , GUI 없음