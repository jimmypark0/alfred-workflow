#!/usr/bin/env python3
import sys
import json
import os
from datetime import datetime, timedelta
from api_client import WantedspaceAPIClient

def main():
    query = sys.argv[1] if len(sys.argv) > 1 else ""
    
    try:
        client = WantedspaceAPIClient()
        items = []
        
        if not query:
            # 기본 메뉴 표시
            today = datetime.now().strftime('%Y-%m-%d')
            
            items = [
                {
                    "uid": "ws-checkin",
                    "title": "🟢 출근하기",
                    "subtitle": "출근 체크인을 진행합니다",
                    "arg": "checkin",
                    "icon": {"path": "icon.png"}
                },
                {
                    "uid": "ws-checkout", 
                    "title": "🔴 퇴근하기",
                    "subtitle": "퇴근 체크아웃을 진행합니다",
                    "arg": "checkout",
                    "icon": {"path": "icon.png"}
                },
                {
                    "uid": "ws-away",
                    "title": "🟡 자리비움",
                    "subtitle": "자리비움 상태로 변경합니다",
                    "arg": "away", 
                    "icon": {"path": "icon.png"}
                },
                {
                    "uid": f"ws-today-{today}",
                    "title": "📊 오늘 현황 보기",
                    "subtitle": f"오늘({today}) 출퇴근 현황을 조회합니다",
                    "arg": f"view:{today}",
                    "icon": {"path": "icon.png"}
                }
            ]
            
        elif query.startswith("view:"):
            # 날짜별 현황 조회
            date = query.replace("view:", "")
            try:
                result = client.get_worktime(date)
                
                if result.get('results'):
                    for worktime in result['results']:
                        formatted = client.format_worktime_display(worktime)
                        items.append({
                            "uid": f"ws-worktime-{worktime.get('email', '')}-{date}",
                            "title": formatted['title'],
                            "subtitle": formatted['subtitle'],
                            "arg": f"detail:{worktime.get('email', '')}:{date}",
                            "icon": {"path": "icon.png"},
                            "mods": {
                                "cmd": {
                                    "subtitle": "상세 정보 보기",
                                    "arg": f"detail:{worktime.get('email', '')}:{date}"
                                }
                            }
                        })
                else:
                    items.append({
                        "uid": "ws-no-data",
                        "title": "데이터 없음",
                        "subtitle": f"{date}에 대한 출퇴근 기록이 없습니다",
                        "arg": "none",
                        "icon": {"path": "icon.png"}
                    })
                    
            except Exception as e:
                items.append({
                    "uid": "ws-error-view",
                    "title": "조회 실패",
                    "subtitle": f"출퇴근 현황 조회 중 오류가 발생했습니다: {str(e)[:50]}",
                    "arg": "error",
                    "icon": {"path": "icon.png"}
                })
                
        elif query in ["checkin", "checkout", "away"]:
            # 출퇴근/자리비움 실행
            action_map = {
                "checkin": ("IN", "출근"),
                "checkout": ("OUT", "퇴근"), 
                "away": ("AWAY", "자리비움")
            }
            check_type, action_name = action_map[query]
            
            try:
                result = client.check_in_out(check_type)
                username = result.get('username', 'Unknown')
                team_name = result.get('team_name', 'Unknown Team')
                
                items.append({
                    "uid": f"ws-success-{query}",
                    "title": f"✅ {action_name} 완료",
                    "subtitle": f"{username} ({team_name}) - {action_name}이 완료되었습니다",
                    "arg": "success",
                    "icon": {"path": "icon.png"}
                })
                
            except Exception as e:
                items.append({
                    "uid": f"ws-error-{query}",
                    "title": f"❌ {action_name} 실패",
                    "subtitle": f"{action_name} 처리 중 오류가 발생했습니다: {str(e)[:50]}",
                    "arg": "error",
                    "icon": {"path": "icon.png"}
                })
                
        elif query.startswith("20") and len(query) == 10:
            # 날짜 형식 입력 (YYYY-MM-DD)
            try:
                datetime.strptime(query, '%Y-%m-%d')
                items.append({
                    "uid": f"ws-view-date-{query}",
                    "title": f"📅 {query} 현황 조회",
                    "subtitle": f"{query}의 출퇴근 현황을 조회합니다",
                    "arg": f"view:{query}",
                    "icon": {"path": "icon.png"}
                })
            except ValueError:
                items.append({
                    "uid": "ws-invalid-date",
                    "title": "잘못된 날짜 형식",
                    "subtitle": "날짜는 YYYY-MM-DD 형식으로 입력해주세요 (예: 2022-06-09)",
                    "arg": "error",
                    "icon": {"path": "icon.png"}
                })
                
        else:
            # 검색어가 있는 경우 날짜 관련 제안
            today = datetime.now().strftime('%Y-%m-%d')
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            
            items = [
                {
                    "uid": f"ws-suggest-today",
                    "title": f"📊 오늘 현황 ({today})",
                    "subtitle": "오늘의 출퇴근 현황을 조회합니다",
                    "arg": f"view:{today}",
                    "icon": {"path": "icon.png"}
                },
                {
                    "uid": f"ws-suggest-yesterday", 
                    "title": f"📊 어제 현황 ({yesterday})",
                    "subtitle": "어제의 출퇴근 현황을 조회합니다",
                    "arg": f"view:{yesterday}",
                    "icon": {"path": "icon.png"}
                },
                {
                    "uid": "ws-suggest-date",
                    "title": "📅 특정 날짜 조회",
                    "subtitle": "YYYY-MM-DD 형식으로 날짜를 입력하세요 (예: 2022-06-09)",
                    "arg": "help",
                    "icon": {"path": "icon.png"}
                }
            ]
            
    except Exception as e:
        # 전체적인 오류 처리
        items = [{
            "uid": "ws-general-error",
            "title": "Wantedspace 워크플로우 오류",
            "subtitle": f"오류가 발생했습니다: {str(e)[:60]}",
            "arg": "error",
            "icon": {"path": "icon.png"}
        }]
    
    result = {"items": items}
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()