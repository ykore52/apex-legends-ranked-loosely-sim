'''
  Apex Legends Season13 のランクをシミュレーションするやつ
'''
import random
import uuid
import pprint

players = []

#全プレイヤー数。本当は40万人で回す必要あり
max_players = 100000

rank_tier = [0, 250, 500, 750, 1000, 1500, 2000, 2500, 3000, 3600, 4200, 4800, 5400, 6100, 6800, 7500, 8200, 9000, 9800, 10600, 11400, 12300, 13200, 14100] + [15000+i*1000 for i in range(30)] + [99999]
rank_fee = [0,0,0,0] + [i*3+15 for i in range(0, 21)]
rank_points = [125, 95, 70, 55, 45, 30, 20, 20, 10, 10, 5, 5, 5, 0, 0, 0, 0, 0, 0, 0]
kill_points = [25, 23, 20, 18, 16, 14, 12, 12, 10, 10, 5, 5, 5, 1, 1, 1, 1, 1, 1, 1]
kill_decay = [1, 1, 1, 0.8, 0.8, 0.8, 0.2]

class Player:
  def __init__(self):
    global pcount
    self.name = "Player_" + str(pcount)
    self.kill = 0
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
  def __init__(self):
    self.squads = []
    self.squads_score = []
    
  def generate_squad(self):
    # TODO: 同じランク帯のマッチングアルゴ
    p_count = 0
    p_list = set()
    while len(list(p_list)) != 60:
        p_list.add( random.randint(0, len(players)-1) )
    p_list = list(p_list)
    random.shuffle(p_list)
    
    for i in range(20):
      sq = [ players[p_list[i*3]], players[p_list[i*3+1]], players[p_list[i*3+2]] ]
      self.squads_score.append( [PlayerScore(), PlayerScore(), PlayerScore()] )
      self.squads.append( sq )
    
  def calc_rank_point(self, kill, assist, rank, rank_point, squad_score):
    try:
      if rank_point >= 15000:
        # マスター以上の参加費計算
        fee = rank_fee[-1] + (rank_point - 15000)/1000*5
        fee = max(175, fee)
      else:
        # ダイヤ以下の参加費計算
        tier_index = -1
        for i in range(len(rank_tier)):
          if rank_tier[i] > rank_point:
            tier_index = i-1
            break
        fee = rank_fee[tier_index]
    except:
      print(kill, assist, rank, rank_fee, tier_index, rank_point, squad_score)
      pprint.pprint(self.squads)
      raise
      
    return int(
      (kill + assist) * kill_points[rank]
      + int((squad_score[0].kill + squad_score[1].kill + squad_score[2].kill - kill) * kill_points[rank] * 0.5)
      + rank_points[rank]
      - fee
    )
  
  def match(self):
    total_kill = 0
    
    while len(self.squads) != 1:
      s1 = 0
      s2 = 0
      while True:
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
        self.squads[loser][i].death += 1
        
        #キルできたら強くなるシステム(要らないと思うが)
        if self.squads_score[loser][i].kill > 0:
          self.squads[loser][i].strength *= 1.01
        
      self.squads.pop(loser)
      self.squads_score.pop(loser)
    
    # calc rank points of champions
    for i in range(3):
      self.squads[0][i].rank_point += self.calc_rank_point(self.squads_score[0][i].kill, self.squads_score[0][i].assist, 0, self.squads[0][i].rank_point, self.squads_score[0])
      
      if self.squads_score[0][i].kill > 0:
        self.squads[0][i].strength *= 1.01

def show_stats(num_game):
  stats = [0 for i in range(len(rank_tier))]
  
  for y in range(0, len(rank_tier)):
    num_player = len(list(filter( lambda x: rank_tier[y] <= x.rank_point and x.rank_point < rank_tier[y+1] , players )))
    stats[y] = num_player / max_players * 100
    
  print("Game: {}".format(num_game))
  for y in range(0, len(rank_tier)):
    print("{}: ".format(str(rank_tier[y]).rjust(5)), end="")
    print(stats[y], end="")
    print("")
  print("------------------")

def generate_player(n):
  for i in range(n):
    players.append( Player() )

def main():
  global pcount
  pcount = 0
  
  generate_player(max_players)
  
  # 100001ゲーム回す
  for i in range(100001):
    ranked = Ranked()
    ranked.generate_squad()
    ranked.match()
    
    # 1000ゲームごとに統計表示
    if i % 1000 == 0:
      show_stats(i)
  
  global players
  p = sorted(players, key=lambda x: x.kill / x.death, reverse=True)
  
  # K/D のトップと最下位の成績を表示してみる
  pprint.pprint(p[0])
  pprint.pprint(p[-1])
main()
