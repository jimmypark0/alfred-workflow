# Wantedspace 출퇴근 관리 Alfred Workflow

Wantedspace API를 사용하여 출퇴근 체크, 자리비움, 현황 조회를 할 수 있는 Alfred 워크플로우입니다.

## 사용법

1. Alfred에서 `ws` 입력
2. 원하는 기능 선택:
   - 🟢 **출근하기**: 출근 체크인
   - 🔴 **퇴근하기**: 퇴근 체크아웃  
   - 🟡 **자리비움**: 자리비움 상태로 변경
   - 📊 **오늘 현황 보기**: 오늘의 출퇴근 현황 조회
   - 📅 **특정 날짜 조회**: YYYY-MM-DD 형식으로 날짜 입력

## 설치

1. Python 의존성 설치:
   ```bash
   pip3 install -r requirements.txt
   ```
2. `config.json`에서 API 설정:
   - `api_key`: 오픈API 키
   - `api_secret`: 오픈API 시크릿키  
   - `default_user.email`: 기본 사용자 이메일
3. `.alfredworkflow` 파일을 더블클릭하여 설치
4. `ws` 키워드로 사용 가능

## 설정

`config.json`에서 다음을 설정할 수 있습니다:
- **API 인증**: `api_key`, `api_secret`
- **기본 사용자**: `default_user.email`
- **표시 설정**: 날짜/시간 포맷, 표시할 정보
- **API 제한**: 요청 타임아웃, 분당 요청 제한

## 주요 기능

- **출퇴근 체크**: 원클릭으로 출근/퇴근 처리
- **자리비움**: 업무 중 자리비움 상태 관리
- **현황 조회**: 날짜별 출퇴근 기록 확인
- **실시간 API**: Wantedspace API와 실시간 연동
- **에러 핸들링**: API 오류 시 적절한 안내 메시지
- **직관적 UI**: 이모지와 한국어로 구성된 사용자 친화적 인터페이스

## API 제한사항

- **호출 제한**: 1분에 30번
- **결과 제한**: 호출당 50개 결과
- **인증**: HTTP Header Authorization + 요청 파라미터 key 필요

## 파일 구조

- `main.py` - 메인 워크플로우 스크립트
- `api_client.py` - Wantedspace API 클라이언트
- `config.json` - 설정 파일
- `requirements.txt` - Python 의존성
- `info.plist` - Alfred 워크플로우 설정

## 필수 조건

- Alfred 4+ with Powerpack
- Python 3 (macOS 기본 설치)
- 인터넷 연결 (API 호출용)
- Wantedspace 오픈API 키/시크릿키