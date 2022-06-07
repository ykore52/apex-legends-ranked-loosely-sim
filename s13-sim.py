'''
  Apex Legends Season13 のランクをシミュレーションするやつ
'''
import random
import uuid
import pprint

players = []

#全プレイヤー数。本当は40万人で回す必要あり
MAX_PLAYERS = 100000
MAX_GAMES = 500000

class Counter:
  def __init__(self):
    self.count = 0
  def inc(self):
    self.count += 1

class RankedSystem_Season13:
  def __init__(self):
    self.tier_rp = [0, 250, 500, 750, 1000, 1500, 2000, 2500, 3000, 3600, 4200, 4800, 5400, 6100, 6800, 7500, 8200, 9000, 9800, 10600, 11400, 12300, 13200, 14100] + [15000+i*1000 for i in range(30)] + [99999]
    self.room_level = [0, 1000, 3000, 5400, 6100, 7500, 9000, 10600, 12300, 14100, 99999]
    self.tier_name = [
      { "name" : "Rookie", "division" : 4, "demotion" : False },
      { "name" : "Rookie", "division" : 3, "demotion" : True },
      { "name" : "Rookie", "division" : 2, "demotion" : True },
      { "name" : "Rookie", "division" : 1, "demotion" : True },
      { "name" : "Bronze", "division" : 4, "demotion" : False },
      { "name" : "Bronze", "division" : 3, "demotion" : True },
      { "name" : "Bronze", "division" : 2, "demotion" : True },
      { "name" : "Bronze", "division" : 1, "demotion" : True },
      { "name" : "Silver", "division" : 4, "demotion" : True },
      { "name" : "Silver", "division" : 3, "demotion" : True },
      { "name" : "Silver", "division" : 2, "demotion" : True },
      { "name" : "Silver", "division" : 1, "demotion" : True },
      { "name" : "Gold", "division" : 4, "demotion" : True },
      { "name" : "Gold", "division" : 3, "demotion" : True },
      { "name" : "Gold", "division" : 2, "demotion" : True },
      { "name" : "Gold", "division" : 1, "demotion" : True },
      { "name" : "Platinum", "division" : 4, "demotion" : True },
      { "name" : "Platinum", "division" : 3, "demotion" : True },
      { "name" : "Platinum", "division" : 2, "demotion" : True },
      { "name" : "Platinum", "division" : 1, "demotion" : True },
      { "name" : "Diamond", "division" : 4, "demotion" : True },
      { "name" : "Diamond", "division" : 3, "demotion" : True },
      { "name" : "Diamond", "division" : 2, "demotion" : True },
      { "name" : "Diamond", "division" : 1, "demotion" : True },
      { "name" : "Master", "division" : 1, "demotion" : True },
      { "name" : "ApexPredetor", "division" : 1, "demotion" : True }
    ]
    self.rank_fee = [0,0,0,0] + [i*3+15 for i in range(0, 21)]
    self.rank_points = [125, 95, 70, 55, 45, 30, 20, 20, 10, 10, 5, 5, 5] + [0 for i in range(50)]
    self.kill_points = [25, 23, 20, 18, 16, 14, 12, 12, 10, 10, 5, 5, 5]  + [1 for i in range(50)]

class Player:
  def __init__(self):
    global pcount
    self.name = "Player_" + str(pcount)
    self.kill = 0
    self.assist = 0
    self.death = 0
    pcount += 1
    
    self.strength = random.normalvariate(1, 0.2)
    self.rank_point = 0
    
  def __repr__(self):
    kv = [f"{key}={value!r}" for key, value in self.__dict__.items()]
    return "{}({})".format(type(self).__name__, ", ".join(kv))

class PlayerScore:
  def __init__(self):
    self.kill = 0
    self.assist = 0
    
  def __repr__(self):
    kv = [f"{key}={value!r}" for key, value in self.__dict__.items()]
    return "{}({})".format(type(self).__name__, ", ".join(kv))

class Ranked:
  def __init__(self, ranked_sys, counter):
    self.squads = []
    self.squads_score = []
    self.system = ranked_sys
    self.counter = counter
    
    self.room = [ {"last_match": 0, "room": set()} for i in range(len(self.system.room_level)) ]
    
  def matchmaking(self):
    matched_room_id = -1
    while True:
      self.counter.inc()
      
      # ランダムに選択したプレイヤーをキューに入れる
      p_id = random.randint(0, len(players)-1)
      room_id = -1
      for i in range(len(self.system.room_level)):
        if players[p_id].rank_point < self.system.room_level[i]:
          room_id = i-1
          break
      self.room[room_id]["room"].add( p_id )
      
      matched = False
      for i in range(len(self.system.room_level)):
        if len(list(self.room[i]["room"])) >= 60:
          # マッチ成立
          matched = True
          matched_room_id = i
          self.room[i]["last_match"] = self.counter.count
          break
      if matched:
        break
      
      # 長時間マッチが成立しない場合は下のランクに吸われる仕組み
      for i in range(len(self.room)-1, 0, -1):
        if self.counter.count - self.room[i]["last_match"] > 500000 and len(list(self.room[i]["room"])) > 0:
          print("Vacuum!!", i)
          print("  from: ", list(map(lambda p: players[p].rank_point, list(self.room[i]["room"]))))
          self.room[i-1]["room"] |= self.room[i]["room"]
          print("    to: ", list(map(lambda p: players[p].rank_point, list(self.room[i-1]["room"]))))
          self.room[i]["room"] = set()
          self.room[i]["last_match"] = int(self.counter.count)
          
    p_list = list(self.room[matched_room_id]["room"])
    first_60 = p_list[:60]
    if len(p_list) > 60:
      p_list = p_list[60:-1]
    else:
      p_list = []
    
    random.shuffle(first_60)
    self.room[matched_room_id]["room"] = set(p_list)
    
    return first_60
  
  def generate_squad(self):
    p_list = self.matchmaking()
    self.squads = []
    for i in range(20):
      sq = [ players[p_list[i*3]], players[p_list[i*3+1]], players[p_list[i*3+2]] ]
      self.squads_score.append( [PlayerScore(), PlayerScore(), PlayerScore()] )
      self.squads.append( sq )
    
  def calc_rank_point(self, kill, assist, rank, rank_point, squad_score):
    if rank_point >= 15000:
      # マスター以上の参加費計算
      fee = self.system.rank_fee[-1] + (rank_point - 15000)/1000*5
      fee = max(175, fee)
    else:
      # ダイヤ以下の参加費計算
      tier_index = -1
      for i in range(len(self.system.tier_rp)):
        if self.system.tier_rp[i] > rank_point:
          tier_index = i-1
          break
      fee = self.system.rank_fee[tier_index]
    
    team_kill = squad_score[0].kill + squad_score[1].kill + squad_score[2].kill - (kill+assist)
    
    if kill + assist >= 7:
      '''
         (a) kp >= 7
             123456789
             kkkkkkktt
      '''
      kp = int(
        3 * self.system.kill_points[rank]
        + 0.8 * 3 * self.system.kill_points[rank]
        + 0.2 * (kill + assist - 6) * self.system.kill_points[rank]
      )
      tp = int(team_kill * self.system.kill_points[rank] * 0.2 * 0.5)
    elif kill + assist >= 4:
      '''
         (a) kp >= 4 and kp + tp >= 7
             123456789
             kkkktttt
         (b) kp >= 4 and kp + tp <= 6
             123456789
             kkkktt
      '''
      kp = int(
        3 * self.system.kill_points[rank]
        + 0.8 * 3 * self.system.kill_points[rank]
      )
      if kill + assist + team_kill >= 7:
        tp = int(
          (6 - (kill+assist)) * self.system.kill_points[rank] * 0.8 * 0.5
          + (team_kill - 6) * self.system.kill_points[rank] * 0.2 * 0.5
        )
      else:
        tp = int(
          team_kill * self.system.kill_points[rank] * 0.8 * 0.5
        )
    else:
      '''
         (a) kp <= 3 and kp + tp >= 7
             123456789
             kkktttt
         (b) kp <= 3 and kp + tp <= 6
             123456789
             kkkttt
         (c) kp <= 3 and kp + tp <= 3
             123456789
             kkt
      '''
      kp = int(3 * self.system.kill_points[rank])
      if kill + assist + team_kill >= 7:
        tp = int(
          (3 - (kill+assist)) * self.system.kill_points[rank] * 0.5
          + (6 - (kill+assist)) * self.system.kill_points[rank] * 0.8 * 0.5
          + (team_kill - 6) * self.system.kill_points[rank] * 0.2 * 0.5
        )
      elif kill + assist + team_kill >= 4:
        tp = int(
          (3 - (kill+assist)) * self.system.kill_points[rank] * 0.5
          + (team_kill - 3) * self.system.kill_points[rank] * 0.8 * 0.5
        )
      else:
        tp = int(
          team_kill * self.system.kill_points[rank] * 0.5
        )
    
    point = int( kp + tp + self.system.rank_points[rank] - fee )
    
    return point
  
  def match(self):
    total_kill = 0
    
    while len(self.squads) != 1:
      s1 = 0
      s2 = 0
      while True:
        self.counter.inc()
        s1 = random.randint(0, len(self.squads)-1)
        s2 = random.randint(0, len(self.squads)-1)
        if s1 != s2:
          break
      
      # 勝ち負けは strength の合計値でざっくり計算
      total_str_s1 = (
        random.uniform(0.7, 2.0) * self.squads[s1][0].strength +
        random.uniform(0.7, 2.0) * self.squads[s1][1].strength +
        random.uniform(0.7, 2.0) * self.squads[s1][2].strength
      )

      total_str_s2 = (
        random.uniform(0.7, 2.0) * self.squads[s2][0].strength +
        random.uniform(0.7, 2.0) * self.squads[s2][1].strength +
        random.uniform(0.7, 2.0) * self.squads[s2][2].strength
      )
      
      if total_str_s1 > total_str_s2:
        winner = s1
        loser = s2
      else:
        winner = s2
        loser = s1
      
      kill_template = [
        [3,0,0],
        [2,1,0],
        [1,1,1]
      ]
      
      kill = 3
      assist = 3
      
      val_o = random.sample([0,1,2], 3)
      kill_order = random.randint(0,2)
      
      self.squads_score[winner][val_o[0]].kill += kill_template[kill_order][0]
      self.squads_score[winner][val_o[1]].kill += kill_template[kill_order][1]
      self.squads_score[winner][val_o[2]].kill += kill_template[kill_order][2]
      
      total_kill += kill_template[kill_order][0] + kill_template[kill_order][1] + kill_template[kill_order][2]
      
      self.squads_score[winner][val_o[0]].assist += random.randint(0, assist - kill_template[kill_order][0])
      self.squads_score[winner][val_o[1]].assist += random.randint(0, assist - kill_template[kill_order][1])
      self.squads_score[winner][val_o[2]].assist += random.randint(0, assist - kill_template[kill_order][2])
      
      # calc rank points of losers
      loser_rank = len(self.squads)-1
      for i in range(3):
        self.squads[loser][i].rank_point += self.calc_rank_point(self.squads_score[loser][i].kill, self.squads_score[loser][i].assist, loser_rank, self.squads[loser][i].rank_point, self.squads_score[loser])
        
        self.squads[loser][i].kill += self.squads_score[loser][i].kill
        self.squads[loser][i].assist += self.squads_score[loser][i].assist
        self.squads[loser][i].death += 1
        
        #キルできたら強くなるシステム(要らないと思うが)
        if self.squads_score[loser][i].kill > 0:
          self.squads[loser][i].strength *= 1.02
        
      self.squads.pop(loser)
      self.squads_score.pop(loser)
    
    # calc rank points of champions
    for i in range(3):
      self.squads[0][i].rank_point += self.calc_rank_point(self.squads_score[0][i].kill, self.squads_score[0][i].assist, 0, self.squads[0][i].rank_point, self.squads_score[0])
      
      self.squads[0][i].kill += self.squads_score[0][i].kill
      self.squads[0][i].assist += self.squads_score[0][i].assist
      
      #キルできたら強くなるシステム(要らないと思うが)
      if self.squads_score[0][i].kill > 0:
        self.squads[0][i].strength *= 1.02

  def show_stats(self, num_game, detail=True):
    if detail:
      stats = [0 for i in range(len(self.system.tier_rp))]
      for y in range(0, len(self.system.tier_rp)):
        num_player = len(list(filter( lambda x: self.system.tier_rp[y] <= x.rank_point and x.rank_point < self.system.tier_rp[y+1] , players )))
        stats[y] = num_player
      
    print("Game: {}, Players: {}".format(num_game, len(players)))
    
    if detail:
      for y in range(0, len(self.system.tier_rp)):
        print("{}: ".format(str(self.system.tier_rp[y]).rjust(5)), end="")
        print("{} {}".format(stats[y], stats[y]/MAX_PLAYERS), end="")
        print("")
      print("------------------")

  def show_result(self):
    stats = [0 for i in range(len(self.system.tier_rp))]
    for y in range(0, len(self.system.tier_rp)):
      num_player = len(list(filter( lambda x: self.system.tier_rp[y] <= x.rank_point and x.rank_point < self.system.tier_rp[y+1] , players )))
      stats[y] = num_player
      
    for y in range(0, len(self.system.tier_rp)):
      print("{}: ".format(str(self.system.tier_rp[y]).rjust(5)), end="")
      print("{} {}".format(stats[y], stats[y]/MAX_PLAYERS), end="")
      print("")
    print("------------------")
    
def generate_player(n):
  for i in range(n):
    players.append( Player() )

def main():
  global pcount
  pcount = 0
  
  generate_player(MAX_PLAYERS)
  
  counter = Counter()
  
  ranked = Ranked( RankedSystem_Season13(), counter )
  for i in range(MAX_GAMES):
    
    ranked.generate_squad()
    ranked.match()
    
    if i % 10000 == 0:
      ranked.show_stats(i, detail=True)
    
    # 1000ゲームごとに新規100人追加
    if i % 1000 == 0:
      generate_player(100)
      
  ranked.show_result()
  
  global players
  p = sorted(players, key=lambda x: x.kill / x.death, reverse=True)
  
  # K/D のトップと最下位の成績を表示してみる
  pprint.pprint(p[0])
  pprint.pprint(p[-1])
  
  p = sorted(players, key=lambda x: x.rank_point, reverse=True)
  
  pprint.pprint(p[0])
  pprint.pprint(p[-1])
main()
