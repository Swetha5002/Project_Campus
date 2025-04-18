import requests
from bs4 import BeautifulSoup
import time

class CodingProfileScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.leetcode_graphql_url = "https://leetcode.com/graphql"
        self.timeout = 10

    def get_leetcode_total_problems(self, username):
        """Get total solved problems count from LeetCode using GraphQL API"""
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
                    print(f"LeetCode user '{username}' not found")
                    return 0

                stats = data['data']['matchedUser']['submitStats']['acSubmissionNum']
                total_solved = next(
                    (item['count'] for item in stats if item['difficulty'] == "All"), 
                    0
                )
                return total_solved
            else:
                print(f"LeetCode API error: {response.status_code}")
                return 0
                
        except Exception as e:
            print(f"Error fetching LeetCode data: {str(e)}")
            return 0

    def get_geeksforgeeks_total_problems(self, username):
        """Get total solved problems count from GeeksforGeeks"""
        url = f'https://auth.geeksforgeeks.org/user/{username}/'
        
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the score cards container
            score_cards = soup.find('div', class_='scoreCards_head__G_uNQ')
            if not score_cards:
                print("GeeksforGeeks score cards section not found")
                return 0
                
            # Find all score card items
            cards = score_cards.find_all('div', class_='scoreCard_head__nxXR8')
            for card in cards:
                # Look for the "Problem Solved" card
                text_div = card.find('div', class_='scoreCard_head_left--text__KZ2S1')
                if text_div and text_div.text.strip().lower() == "problem solved":
                    score_div = card.find('div', class_='scoreCard_head_left--score__oSi_x')
                    if score_div:
                        try:
                            return int(score_div.text.strip())
                        except ValueError:
                            print("Could not convert problems count to integer")
                            return 0
            
            print("Problems solved card not found in score cards")
            return 0
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching GeeksforGeeks data: {str(e)}")
            return 0
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return 0

    def get_all_stats(self, leetcode_username, geeksforgeeks_username):
        """Get combined stats from both platforms"""
        print(f"\nFetching coding profile stats...")
        print(f"LeetCode username: {leetcode_username}")
        print(f"GeeksforGeeks username: {geeksforgeeks_username}")
        
        start_time = time.time()
        
        leetcode_count = self.get_leetcode_total_problems(leetcode_username)
        geeksforgeeks_count = self.get_geeksforgeeks_total_problems(geeksforgeeks_username)
        total_count = leetcode_count + geeksforgeeks_count
        
        elapsed_time = round(time.time() - start_time, 2)
        
        print("\nResults:")
        print(f"- LeetCode problems solved: {leetcode_count}")
        print(f"- GeeksforGeeks problems solved: {geeksforgeeks_count}")
        print(f"- Total problems solved: {total_count}")
        print(f"\nCompleted in {elapsed_time}s")
        
        return {
            "leetcode": leetcode_count,
            "geeksforgeeks": geeksforgeeks_count,
            "total": total_count
        }


# Example Usage
if __name__ == "__main__":
    scraper = CodingProfileScraper()
    
    # Test with sample usernames
    stats = scraper.get_all_stats(
        leetcode_username="lA1xrflaUy",
        geeksforgeeks_username="vimalrajnaggo03"
    )
    
    # Example output usage
    print("\nReturned data structure:")
    print(stats)