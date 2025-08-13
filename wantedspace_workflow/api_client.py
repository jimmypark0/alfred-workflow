#!/usr/bin/env python3
import json
import os
import requests
from datetime import datetime
from typing import List, Dict, Optional

class WantedspaceAPIClient:
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.base_url = self.config['api']['base_url']
        self.timeout = self.config['api']['timeout']
        self.api_key = self.config['auth']['api_key']
        self.api_secret = self.config['auth']['api_secret']
        self.default_email = self.config['default_user']['email']
        
        self.headers = {
            'User-Agent': self.config['auth']['user_agent'],
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        if self.api_secret:
            self.headers['Authorization'] = self.api_secret
    
    def _make_get_request(self, endpoint: str, params: Dict = None) -> Dict:
        url = f"{self.base_url}{endpoint}"
        params = params or {}
        if self.api_key:
            params['key'] = self.api_key
            
        try:
            response = requests.get(
                url,
                headers=self.headers,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API GET request failed: {str(e)}")
    
    def _make_post_request(self, endpoint: str, data: Dict = None) -> Dict:
        url = f"{self.base_url}{endpoint}"
        data = data or {}
        if self.api_key:
            data['key'] = self.api_key
            
        try:
            response = requests.post(
                url,
                headers=self.headers,
                json=data,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API POST request failed: {str(e)}")
    
    def _make_put_request(self, endpoint: str, data: Dict = None) -> str:
        url = f"{self.base_url}{endpoint}"
        data = data or {}
        if self.api_key:
            data['key'] = self.api_key
            
        try:
            response = requests.put(
                url,
                headers=self.headers,
                json=data,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            raise Exception(f"API PUT request failed: {str(e)}")
    
    def _make_delete_request(self, endpoint: str, params: Dict = None) -> str:
        url = f"{self.base_url}{endpoint}"
        params = params or {}
        if self.api_key:
            params['key'] = self.api_key
            
        try:
            response = requests.delete(
                url,
                headers=self.headers,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            raise Exception(f"API DELETE request failed: {str(e)}")
    
    def get_worktime(self, date: str, email: str = None) -> Dict:
        """출퇴근 현황 조회"""
        endpoint = self.config['endpoints']['worktime_get']
        params = {'date': date}
        if email:
            params['email'] = email
        
        return self._make_get_request(endpoint, params)
    
    def check_in_out(self, check_type: str, email: str = None) -> Dict:
        """출근/퇴근/자리비움 신청
        check_type: IN (출근), OUT (퇴근), AWAY (자리비움)
        """
        endpoint = self.config['endpoints']['worktime_post']
        data = {
            'check_type': check_type,
            'email': email or self.default_email
        }
        
        return self._make_post_request(endpoint, data)
    
    def update_worktime(self, email: str, wk_date: str, 
                       wk_start_time: str = None, wk_end_time: str = None,
                       wk_memo: str = None, work_except: List[Dict] = None) -> str:
        """출퇴근 수정"""
        endpoint = self.config['endpoints']['worktime_update']
        data = {
            'email': email or self.default_email,
            'wk_date': wk_date
        }
        
        if wk_start_time:
            data['wk_start_time'] = wk_start_time
        if wk_end_time:
            data['wk_end_time'] = wk_end_time
        if wk_memo:
            data['wk_memo'] = wk_memo
        if work_except:
            data['work_except'] = work_except
            
        return self._make_put_request(endpoint, data)
    
    def delete_worktime(self, email: str, wk_date: str) -> str:
        """출퇴근 삭제"""
        endpoint = self.config['endpoints']['worktime_delete'].format(email=email)
        params = {'wk_date': wk_date}
        
        return self._make_delete_request(endpoint, params)
    
    def format_worktime_display(self, worktime_data: Dict) -> Dict:
        """출퇴근 데이터를 Alfred 표시용으로 포맷"""
        username = worktime_data.get('username', 'Unknown')
        team_name = worktime_data.get('team_name', 'Unknown Team')
        
        # 시간 포맷팅
        start_time = worktime_data.get('wk_start_time')
        end_time = worktime_data.get('wk_end_time')
        
        if start_time:
            start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00')).strftime('%H:%M')
        else:
            start_time = '-'
            
        if end_time:
            end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00')).strftime('%H:%M')
        else:
            end_time = '-'
        
        # 근무시간 (분 -> 시간:분)
        wk_time = worktime_data.get('wk_time_today', worktime_data.get('wk_time', 0))
        hours = wk_time // 60
        minutes = wk_time % 60
        
        # 승인 상태
        approval = worktime_data.get('wk_approved', 'NUL_IN/NUL_OUT')
        approval_display = approval.replace('APV', '승인').replace('REQ', '요청').replace('DNY', '반려').replace('NUL', '대기')
        
        return {
            'title': f"{username} ({team_name})",
            'subtitle': f"출근: {start_time} | 퇴근: {end_time} | 근무: {hours}h {minutes}m | {approval_display}",
            'details': worktime_data
        }