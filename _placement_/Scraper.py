# scraper.py
import requests
from bs4 import BeautifulSoup
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta

User = get_user_model()

class DSAScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.leetcode_graphql_url = "https://leetcode.com/graphql"
        self.timeout = 10

    def get_leetcode_total(self, username):
        """Get total solved problems count from LeetCode"""
        if not username:
            return 0
            
        query = """
        query getUserProfile($username: String!) {
          matchedUser(username: $username) {
            submitStats {
              acSubmissionNum {
                difficulty
                count
              }
            }
          }
        }
        """
        variables = {"username": username}
        
        try:
            response = requests.post(
                self.leetcode_graphql_url,
                json={"query": query, "variables": variables},
                headers=self.headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                if not data.get('data', {}).get('matchedUser'):
                    return 0

                stats = data['data']['matchedUser']['submitStats']['acSubmissionNum']
                return next((item['count'] for item in stats if item['difficulty'] == "All"), 0)
            return 0
        except Exception as e:
            return 0

    def get_gfg_total(self, username):
        """Get total solved problems count from GeeksforGeeks"""
        if not username:
            return 0
            
        url = f'https://auth.geeksforgeeks.org/user/{username}/'
        
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            soup = BeautifulSoup(response.text, 'html.parser')
            score_cards = soup.find('div', class_='scoreCards_head__G_uNQ')
            if not score_cards:
                return 0
                
            for card in score_cards.find_all('div', class_='scoreCard_head__nxXR8'):
                text_div = card.find('div', class_='scoreCard_head_left--text__KZ2S1')
                if text_div and text_div.text.strip().lower() == "problem solved":
                    score_div = card.find('div', class_='scoreCard_head_left--score__oSi_x')
                    if score_div:
                        try:
                            return int(score_div.text.strip())
                        except ValueError:
                            return 0
            return 0
        except Exception as e:
            return 0

def update_user_dsa_count(user):
    """
    Update DSA count for a single user if not updated today
    Returns: tuple (updated: bool, total_count: int)
    """
    if not (user.leetcode_link or user.gfg_link):
        return user.dsa_problem_solved_count
        
    
    scraper = DSAScraper()
    leetcode_username = user.leetcode_link.split('/')[-1] if user.leetcode_link else None
    gfg_username = user.gfg_link.split('/')[-1] if user.gfg_link else None
    
    leetcode_count = scraper.get_leetcode_total(leetcode_username)
    gfg_count = scraper.get_gfg_total(gfg_username)
    total = leetcode_count + gfg_count
    
    user.dsa_problem_solved_count = total
    user.dsa_last_updated = timezone.now()
    user.save()
    

