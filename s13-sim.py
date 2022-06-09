'''
  Apex Legends Season13 のランクをシミュレーションするやつ
'''
import random
import uuid
import pprint

players = []

#全プレイヤー数。本当は40万人で回す必要あり
MAX_PLAYERS = 50000
MAX_GAMES = 500000

MAX_RP = 9999999

class Counter:
  def __init__(self):
    self.count = 0
  def inc(self):
    self.count += 1


class Player:
  def __init__(self):
    global pcount
    self.name = "Player_" + str(pcount)
    self.kill = 0
    self.assist = 0
    self.death = 0
    self.game = 0
    pcount += 1
    
    self.strength = random.normalvariate(1, 0.2)
    self.rank_point = 0
    self.rank_tier_index = 0
    
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


import dataclasses

@dataclasses.dataclass
class RankedData:
  player : object()
  kill : int
  assist : int
  rank : int
  rank_point : int


@dataclasses.dataclass
class RankedS11_DTO(RankedData):
  pass


@dataclasses.dataclass
class RankedS12_DTO(RankedS11_DTO):
  pass


@dataclasses.dataclass
class RankedS13_DTO(RankedData):
  squad_score : object()


class RankedSystemBase:
  def __init__(self):
    self.season = 0
    self.tier_rp = []
    self.room_level = []
    self.rank_tiers = []
    self.rank_entry_cost = []
    self.rank_points = []
    self.kill_points = []

  def update_rank(self, player):
    if player.rank_point < self.rank_tiers[ player.rank_tier_index ]["needed_point"]:
      if self.rank_tiers[ player.rank_tier_index ]["demotion"]:
        player.rank_tier_index -= 1
    elif self.rank_tiers[player.rank_tier_index]["name"] != "Master" or self.rank_tiers[player.rank_tier_index]["name"] != "ApexPredetor":
      if player.rank_point >= self.rank_tiers[ player.rank_tier_index+1 ]["needed_point"]:
        player.rank_tier_index += 1


class RankedSystem_Season11Base(RankedSystemBase):
  def __init__(self):
    # Max 175 Kill/Assist RP
    self.max_kp = 175
    
  def calc_rank_point(self, data : RankedS11_DTO):
    player = data.player
    kill = data.kill
    assist = data.assist
    rank = data.rank
    rank_point = data.rank_point
    
    # ランク参加費の計算
    tier_index = -1
    for i in range(len(self.tier_rp)):
      if self.tier_rp[i] > rank_point:
        tier_index = i-1
        break
    entry_cost = self.rank_entry_cost[tier_index]
    
    kp = min(self.max_kp, (kill + assist) * self.kill_points[rank])
    
    point = int( kp + self.rank_points[rank] - entry_cost )
    
    # 降格保護
    if point < 0 and player.rank_point + point < self.rank_tiers[ player.rank_tier_index]["needed_point"]:
      if not self.rank_tiers[ player.rank_tier_index ]["demotion"]:
        point = self.rank_tiers[ player.rank_tier_index]["needed_point"] - player.rank_point
    
    player.rank_point += point


class RankedSystem_Season11(RankedSystem_Season11Base):
  def __init__(self):
    self.season = 11
    self.max_kp = 175
    self.tier_rp = [0, 300, 600, 900, 1200, 1600, 2000, 2400, 2800, 3300, 3800, 4300, 4800, 5400, 6000, 6600, 7200, 7900, 8600, 9300, 10000] + [MAX_RP]
    self.room_level = [0, 1000, 3000, 5400, 6100, 7500, 9000, 10600, 12300, 14100, 99999]
    self.rank_tiers = [
      { "index": 0, "rank": 1, "division" : 4, "name" : "Bronze4", "needed_point": 0, "demotion" : False },
      { "index": 1, "rank": 1, "division" : 3, "name" : "Bronze3", "needed_point": 300, "demotion" : True },
      { "index": 2, "rank": 1, "division" : 2, "name" : "Bronze2", "needed_point": 600, "demotion" : True },
      { "index": 3, "rank": 1, "division" : 1, "name" : "Bronze1", "needed_point": 900, "demotion" : True },
      { "index": 4, "rank": 2, "division" : 4, "name" : "Silver4", "needed_point": 1200, "demotion" : False },
      { "index": 5, "rank": 2, "division" : 3, "name" : "Silver3", "needed_point": 1600, "demotion" : True },
      { "index": 6, "rank": 2, "division" : 2, "name" : "Silver2", "needed_point": 2000, "demotion" : True },
      { "index": 7, "rank": 2, "division" : 1, "name" : "Silver1", "needed_point": 2400, "demotion" : True },
      { "index": 8, "rank": 3, "division" : 4, "name" : "Gold4", "needed_point": 2800, "demotion" : False },
      { "index": 9, "rank": 3, "division" : 3, "name" : "Gold3", "needed_point": 3300, "demotion" : True },
      { "index": 10, "rank": 3, "division" : 2, "name" : "Gold2", "needed_point": 3800, "demotion" : True },
      { "index": 11, "rank": 3, "division" : 1, "name" : "Gold1", "needed_point": 4300, "demotion" : True },
      { "index": 12, "rank": 4, "division" : 4, "name" : "Platinum4", "needed_point": 4800, "demotion" : False },
      { "index": 13, "rank": 4, "division" : 3, "name" : "Platinum3", "needed_point": 5400, "demotion" : True },
      { "index": 14, "rank": 4, "division" : 2, "name" : "Platinum2", "needed_point": 6000, "demotion" : True },
      { "index": 15, "rank": 4, "division" : 1, "name" : "Platinum1", "needed_point": 6600, "demotion" : True },
      { "index": 16, "rank": 5, "division" : 4, "name" : "Diamond4", "needed_point": 7200, "demotion" : False },
      { "index": 17, "rank": 5, "division" : 3, "name" : "Diamond3", "needed_point": 7900, "demotion" : True },
      { "index": 18, "rank": 5, "division" : 2, "name" : "Diamond2", "needed_point": 8600, "demotion" : True },
      { "index": 19, "rank": 5, "division" : 1, "name" : "Diamond1", "needed_point": 9300, "demotion" : True },
      { "index": 20, "rank": 6, "division" : 1, "name" : "Master", "needed_point": 10000, "demotion" : False },
      { "index": 21, "rank": 6, "division" : 1, "name" : "ApexPredetor", "needed_point": 10000, "demotion" : True },
      { "index": 99999, "rank": 99999, "division" : 1, "name" : "", "needed_point": MAX_RP, "demotion" : True }
    ]
    self.rank_entry_cost = [0,0,0,0] + [12,12,12,12] + [24,24,24,24] + [36,36,36,36] + [48,48,48,48] + [60, 60]
    self.rank_points = [100, 60, 40, 40, 30, 30, 20, 20, 10, 10, 5, 5, 5] + [0 for i in range(50)]
    self.kill_points = [25, 21, 18, 15, 15, 11, 11, 11, 11, 11] + [10 for i in range(60)]


class RankedSystem_Season12(RankedSystem_Season11Base):
  def __init__(self):
    self.season = 12
    self.max_kp = 125
    self.tier_rp = [0, 300, 600, 900, 1200, 1600, 2000, 2400, 2800, 3300, 3800, 4300, 4800, 5400, 6000, 6600, 7200, 7900, 8600, 9300, 10000] + [MAX_RP]
    self.room_level = [0, 1000, 3000, 5400, 6100, 7500, 9000, 10600, 12300, 14100, 99999]
    self.rank_tiers = [
      { "index": 0, "rank": 1, "division" : 4, "name" : "Bronze4", "needed_point": 0, "demotion" : False },
      { "index": 1, "rank": 1, "division" : 3, "name" : "Bronze3", "needed_point": 300, "demotion" : True },
      { "index": 2, "rank": 1, "division" : 2, "name" : "Bronze2", "needed_point": 600, "demotion" : True },
      { "index": 3, "rank": 1, "division" : 1, "name" : "Bronze1", "needed_point": 900, "demotion" : True },
      { "index": 4, "rank": 2, "division" : 4, "name" : "Silver4", "needed_point": 1200, "demotion" : False },
      { "index": 5, "rank": 2, "division" : 3, "name" : "Silver3", "needed_point": 1600, "demotion" : True },
      { "index": 6, "rank": 2, "division" : 2, "name" : "Silver2", "needed_point": 2000, "demotion" : True },
      { "index": 7, "rank": 2, "division" : 1, "name" : "Silver1", "needed_point": 2400, "demotion" : True },
      { "index": 8, "rank": 3, "division" : 4, "name" : "Gold4", "needed_point": 2800, "demotion" : False },
      { "index": 9, "rank": 3, "division" : 3, "name" : "Gold3", "needed_point": 3300, "demotion" : True },
      { "index": 10, "rank": 3, "division" : 2, "name" : "Gold2", "needed_point": 3800, "demotion" : True },
      { "index": 11, "rank": 3, "division" : 1, "name" : "Gold1", "needed_point": 4300, "demotion" : True },
      { "index": 12, "rank": 4, "division" : 4, "name" : "Platinum4", "needed_point": 4800, "demotion" : False },
      { "index": 13, "rank": 4, "division" : 3, "name" : "Platinum3", "needed_point": 5400, "demotion" : True },
      { "index": 14, "rank": 4, "division" : 2, "name" : "Platinum2", "needed_point": 6000, "demotion" : True },
      { "index": 15, "rank": 4, "division" : 1, "name" : "Platinum1", "needed_point": 6600, "demotion" : True },
      { "index": 16, "rank": 5, "division" : 4, "name" : "Diamond4", "needed_point": 7200, "demotion" : False },
      { "index": 17, "rank": 5, "division" : 3, "name" : "Diamond3", "needed_point": 7900, "demotion" : True },
      { "index": 18, "rank": 5, "division" : 2, "name" : "Diamond2", "needed_point": 8600, "demotion" : True },
      { "index": 19, "rank": 5, "division" : 1, "name" : "Diamond1", "needed_point": 9300, "demotion" : True },
      { "index": 20, "rank": 6, "division" : 1, "name" : "Master", "needed_point": 10000, "demotion" : False },
      { "index": 21, "rank": 6, "division" : 1, "name" : "ApexPredetor", "needed_point": 10000, "demotion" : True },
      { "index": 99999, "rank": 99999, "division" : 1, "name" : "", "needed_point": MAX_RP, "demotion" : True }
    ]
    self.rank_entry_cost = [0,0,0,0] + [12,12,12,12] + [24,24,24,24] + [36,36,36,36] + [48,48,48,48] + [60, 60]
    self.rank_points = [125, 95, 70, 55, 45, 30, 20, 20, 10, 10, 5, 5, 5] + [0 for i in range(50)]
    self.kill_points = [25, 21, 18, 15, 15, 11, 11, 11, 11, 11] + [10 for i in range(60)]


class RankedSystem_Season13(RankedSystemBase):
  def __init__(self):
    self.season = 13
    self.tier_rp = [0, 250, 500, 750, 1000, 1500, 2000, 2500, 3000, 3600, 4200, 4800, 5400, 6100, 6800, 7500, 8200, 9000, 9800, 10600, 11400, 12300, 13200, 14100] + [15000+i*1000 for i in range(30)] + [MAX_RP]
    self.room_level = [0, 1000, 3000, 5400, 6100, 7500, 9000, 10600, 12300, 14100, 99999]
    self.rank_tiers = [
      { "index": 0, "rank": 0, "division" : 4, "name" : "Rookie4", "needed_point": 0, "demotion" : False },
      { "index": 1, "rank": 0, "division" : 3, "name" : "Rookie3", "needed_point": 250, "demotion" : True },
      { "index": 2, "rank": 0, "division" : 2, "name" : "Rookie2", "needed_point": 500, "demotion" : True },
      { "index": 3, "rank": 0, "division" : 1, "name" : "Rookie1", "needed_point": 750, "demotion" : True },
      { "index": 4, "rank": 1, "division" : 4, "name" : "Bronze4", "needed_point": 1000, "demotion" : False },
      { "index": 5, "rank": 1, "division" : 3, "name" : "Bronze3", "needed_point": 1500, "demotion" : True },
      { "index": 6, "rank": 1, "division" : 2, "name" : "Bronze2", "needed_point": 2000, "demotion" : True },
      { "index": 7, "rank": 1, "division" : 1, "name" : "Bronze1", "needed_point": 2500, "demotion" : True },
      { "index": 8, "rank": 2, "division" : 4, "name" : "Silver4", "needed_point": 3000, "demotion" : True },
      { "index": 9, "rank": 2, "division" : 3, "name" : "Silver3", "needed_point": 3600, "demotion" : True },
      { "index": 10, "rank": 2, "division" : 2, "name" : "Silver2", "needed_point": 4200, "demotion" : True },
      { "index": 11, "rank": 2, "division" : 1, "name" : "Silver1", "needed_point": 4800, "demotion" : True },
      { "index": 12, "rank": 3, "division" : 4, "name" : "Gold4", "needed_point": 5400, "demotion" : True },
      { "index": 13, "rank": 3, "division" : 3, "name" : "Gold3", "needed_point": 6100, "demotion" : True },
      { "index": 14, "rank": 3, "division" : 2, "name" : "Gold2", "needed_point": 6800, "demotion" : True },
      { "index": 15, "rank": 3, "division" : 1, "name" : "Gold1", "needed_point": 7500, "demotion" : True },
      { "index": 16, "rank": 4, "division" : 4, "name" : "Platinum4", "needed_point": 8200, "demotion" : True },
      { "index": 17, "rank": 4, "division" : 3, "name" : "Platinum3", "needed_point": 9000, "demotion" : True },
      { "index": 18, "rank": 4, "division" : 2, "name" : "Platinum2", "needed_point": 9800, "demotion" : True },
      { "index": 19, "rank": 4, "division" : 1, "name" : "Platinum1", "needed_point": 10600, "demotion" : True },
      { "index": 20, "rank": 5, "division" : 4, "name" : "Diamond4", "needed_point": 11400, "demotion" : True },
      { "index": 21, "rank": 5, "division" : 3, "name" : "Diamond3", "needed_point": 12300, "demotion" : True },
      { "index": 22, "rank": 5, "division" : 2, "name" : "Diamond2", "needed_point": 13200, "demotion" : True },
      { "index": 23, "rank": 5, "division" : 1, "name" : "Diamond1", "needed_point": 14100, "demotion" : True },
      { "index": 24, "rank": 6, "division" : 1, "name" : "Master", "needed_point": 15000, "demotion" : True },
      { "index": 25, "rank": 6, "division" : 1, "name" : "ApexPredetor", "needed_point": 15000, "demotion" : True },
      { "index": 99999, "rank": MAX_RP, "division" : 1, "name" : "", "needed_point": MAX_RP, "demotion" : True }
    ]
    self.rank_entry_cost = [0,0,0,0] + [i*3+15 for i in range(0, 21)]
    self.rank_points = [125, 95, 70, 55, 45, 30, 20, 20, 10, 10, 5, 5, 5] + [0 for i in range(50)]
    self.kill_points = [25, 23, 20, 18, 16, 14, 12, 12, 10, 10, 5, 5, 5]  + [1 for i in range(50)]
    
  
  def calc_rank_point(self, data : RankedS13_DTO):
    player = data.player
    kill = data.kill
    assist = data.assist
    rank = data.rank
    rank_point = data.rank_point
    squad_score = data.squad_score
    
    # ランク参加費の計算
    if rank_point >= 15000:
      # マスター以上の参加費計算
      entry_cost = self.system.rank_entry_cost[-1] + (rank_point - 15000)/1000*5
      entry_cost = max(175, entry_cost)
    else:
      # ダイヤ以下の参加費計算
      tier_index = -1
      for i in range(len(self.system.tier_rp)):
        if self.system.tier_rp[i] > rank_point:
          tier_index = i-1
          break
      entry_cost = self.system.rank_entry_cost[tier_index]
    
    team_kill = squad_score[0].kill + squad_score[1].kill + squad_score[2].kill - (kill+assist)
    
    if kill + assist >= 7:
      '''
         (a) kp >= 7
             123456789
             kkkkkkktt
      '''
      kp = int(
        3 * self.kill_points[rank]
        + 0.8 * 3 * self.kill_points[rank]
        + 0.2 * (kill + assist - 6) * self.kill_points[rank]
      )
      tp = int(team_kill * self.kill_points[rank] * 0.2 * 0.5)
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
        3 * self.kill_points[rank]
        + 0.8 * 3 * self.kill_points[rank]
      )
      if kill + assist + team_kill >= 7:
        tp = int(
          (6 - (kill+assist)) * self.kill_points[rank] * 0.8 * 0.5
          + (team_kill - 6) * self.kill_points[rank] * 0.2 * 0.5
        )
      else:
        tp = int(
          team_kill * self.kill_points[rank] * 0.8 * 0.5
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
      kp = int(3 * self.kill_points[rank])
      if kill + assist + team_kill >= 7:
        tp = int(
          (3 - (kill+assist)) * self.kill_points[rank] * 0.5
          + (6 - (kill+assist)) * self.kill_points[rank] * 0.8 * 0.5
          + (team_kill - 6) * self.kill_points[rank] * 0.2 * 0.5
        )
      elif kill + assist + team_kill >= 4:
        tp = int(
          (3 - (kill+assist)) * self.kill_points[rank] * 0.5
          + (team_kill - 3) * self.kill_points[rank] * 0.8 * 0.5
        )
      else:
        tp = int(
          team_kill * self.kill_points[rank] * 0.5
        )
    
    point = int( kp + tp + self.rank_points[rank] - entry_cost )
    player.rank_point += point
    
  def update_rank(self, player):
    if player.rank_point < self.rank_tiers[ player.rank_tier_index ]["needed_point"]:
      player.rank_tier_index -= 1
    elif self.rank_tiers[player.rank_tier_index]["name"] != "Master" or self.rank_tiers[player.rank_tier_index]["name"] != "ApexPredetor":
      if player.rank_point >= self.rank_tiers[ player.rank_tier_index+1 ]["needed_point"]:
        player.rank_tier_index += 1


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
      max_p = len(players)
      p_id = random.randint(0, max_p-1)
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
#          print("Vacuum!!", i)
#          print("  from: ", list(map(lambda p: players[p].rank_point, list(self.room[i]["room"]))))
          self.room[i-1]["room"] |= self.room[i]["room"]
#          print("    to: ", list(map(lambda p: players[p].rank_point, list(self.room[i-1]["room"]))))
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
  
  def generate_squads(self):
    p_list = self.matchmaking()
    self.squads = []
    for i in range(20):
      sq = [ players[p_list[i*3]], players[p_list[i*3+1]], players[p_list[i*3+2]] ]
      self.squads_score.append( [PlayerScore(), PlayerScore(), PlayerScore()] )
      self.squads.append( sq )
  
  def fight(self):
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
      random.uniform(0.7, 1.5) * self.squads[s1][0].strength +
      random.uniform(0.7, 1.5) * self.squads[s1][1].strength +
      random.uniform(0.7, 1.5) * self.squads[s1][2].strength
    )

    total_str_s2 = (
      random.uniform(0.7, 1.5) * self.squads[s2][0].strength +
      random.uniform(0.7, 1.5) * self.squads[s2][1].strength +
      random.uniform(0.7, 1.5) * self.squads[s2][2].strength
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
    
    order_valuable = random.sample([0,1,2], 3)
    order_kill = random.randint(0,2)
    
    for i in range(3):
      self.squads_score[winner][order_valuable[i]].kill += kill_template[order_kill][i]
      self.squads_score[winner][order_valuable[i]].assist += random.randint(0, assist - kill_template[order_kill][i])
      
    return (winner, loser)
  
  def match(self):
    while len(self.squads) != 1:
      winner, loser = self.fight()
      
      # calc rank points of losers
      loser_rank = len(self.squads)-1
      for i in range(3):
      
        if self.system.season == 11:
          ranked_data = RankedS11_DTO(
            player = self.squads[loser][i],
            kill = self.squads_score[loser][i].kill,
            assist = self.squads_score[loser][i].assist,
            rank = loser,
            rank_point = self.squads[loser][i].rank_point
          )
        elif self.system.season == 12:
          ranked_data = RankedS12_DTO(
            player = self.squads[loser][i],
            kill = self.squads_score[loser][i].kill,
            assist = self.squads_score[loser][i].assist,
            rank = loser_rank,
            rank_point = self.squads[loser][i].rank_point
          )
        elif self.system.season == 13:
          ranked_data = RankedS13_DTO(
            player = self.squads[loser][i],
            kill = self.squads_score[loser][i].kill,
            assist = self.squads_score[loser][i].assist,
            rank = loser_rank,
            rank_point = self.squads[loser][i].rank_point,
            squad_score = self.squads_score[loser]
          )
        else:
          raise
          
        self.system.calc_rank_point(ranked_data)
        
        self.squads[loser][i].kill += ranked_data.kill
        self.squads[loser][i].assist += ranked_data.assist
        self.squads[loser][i].death += 1
        self.squads[loser][i].game += 1
        self.system.update_rank( self.squads[loser][i] )
        
        #キルできたら強くなるシステム(要らないと思うが)
#        if ranked_data.kill > 0:
#          self.squads[loser][i].strength *= 1.02
        
      self.squads.pop(loser)
      self.squads_score.pop(loser)
    
    # calc rank points of champions
    champion = 0
    for i in range(3):
      
      if self.system.season == 11:
        ranked_data = RankedS11_DTO(
          player = self.squads[champion][i],
          kill = self.squads_score[champion][i].kill,
          assist = self.squads_score[champion][i].assist,
          rank = champion,
          rank_point = self.squads[champion][i].rank_point
        )
      elif self.system.season == 12:
        ranked_data = RankedS12_DTO(
          player = self.squads[champion][i],
          kill = self.squads_score[champion][i].kill,
          assist = self.squads_score[champion][i].assist,
          rank = champion,
          rank_point = self.squads[champion][i].rank_point
        )
      elif self.system.season == 13:
        ranked_data = RankedS13_DTO(
          player = self.squads[champion][i],
          kill = self.squads_score[champion][i].kill,
          assist = self.squads_score[champion][i].assist,
          rank = champion,
          rank_point = self.squads[champion][i].rank_point,
          squad_score = self.squads_score[champion]
        )
      else:
        raise
        
      self.system.calc_rank_point(ranked_data)
      
      self.squads[champion][i].kill += ranked_data.kill
      self.squads[champion][i].assist += ranked_data.assist
      self.squads[champion][i].game += 1
      self.system.update_rank( self.squads[champion][i] )
      
      #キルできたら強くなるシステム(要らないと思うが)
#      if ranked_data.kill > 0:
#        self.squads[champion][i].strength *= 1.02

  def display_stats(self, num_game, detail=True):
    max_p = len(players)
    if detail:
      stats = [0 for i in range(len(self.system.tier_rp))]
      for p in range(max_p):
        for y in range(0, len(self.system.tier_rp)):
          if self.system.tier_rp[y] <= players[p].rank_point and players[p].rank_point < self.system.tier_rp[y+1]:
            stats[y] += 1
            break
      
    print("Season: {}, Game: {}/{}, Players: {}".format(self.system.season, num_game, MAX_GAMES, max_p))
    
    if detail:
      sep_count = Counter()
      sep_count.inc()
      for y in range(0, len(self.system.tier_rp)):
        print("{}: ".format(str(self.system.tier_rp[y]).rjust(7)), end="")
        print("{} {:.03f}".format(str(stats[y]).rjust(6), stats[y]/max_p), end="")
        print("")
        if sep_count.count % 4 == 0:
          print("-----")
        sep_count.inc()
      print("------------------")

  def display_result(self):
    max_p = len(players)
    stats = [0 for i in range(len(self.system.tier_rp))]
    for p in range(max_p):
      for y in range(0, len(self.system.tier_rp)):
        if self.system.tier_rp[y] <= players[p].rank_point and players[p].rank_point < self.system.tier_rp[y+1]:
          stats[y] += 1
          break
      
    print("Season: {}, TotalGame: {}, Players: {}".format(self.system.season, MAX_GAMES, max_p))

    sep_count = Counter()
    sep_count.inc()
    for y in range(0, len(self.system.tier_rp)):
      print("{}: ".format(str(self.system.tier_rp[y]).rjust(7)), end="")
      print("{} {:.03f}".format(str(stats[y]).rjust(6), stats[y]/max_p), end="")
      print("")
      if sep_count.count % 4 == 0:
        print("-----")
      sep_count.inc()
    print("------------------")
    
def generate_player(n):
  global MAX_PLAYERS
  for i in range(n):
    players.append( Player() )
    MAX_PLAYERS += 1

def main():
  global pcount
  pcount = 0
  
  generate_player(MAX_PLAYERS)
  
  counter = Counter()
  
  ranked = Ranked( RankedSystem_Season13(), counter )
  for i in range(MAX_GAMES):
    
    ranked.generate_squads()
    ranked.match()
    
    if i % 10000 == 0:
      ranked.display_stats(i, detail=True)
    
    # 1000ゲームごとに新規追加
    if i % 1000 == 0:
      generate_player(500)
      
  ranked.display_result()
  
  global players
  p = sorted(players, key=lambda x: x.kill / max(1, x.death), reverse=True)
  
  # K/D のトップと最下位の成績を表示してみる
  pprint.pprint(p[0])
  pprint.pprint(p[-1])
  
  p = sorted(players, key=lambda x: x.rank_point, reverse=True)
  
  pprint.pprint(p[0])
  pprint.pprint(p[-1])
main()
