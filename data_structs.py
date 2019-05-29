class User:
    """docstring for User"""

    def __init__(self, email='None', password='None', name='None',
                 last_name='None', last_last_name='None', city='None', suburb='None',
                 street='None', no=0, phone='0', ocupation='admin', id_user='0', id_league='1'):
        self.id_user = id_user
        self.password = password
        self.name = name
        self.last_name = last_name
        self.last_last_name = last_last_name
        self.city = city
        self.suburb = suburb
        self.street = street
        self.no = no
        self.email = email
        self.phone = phone
        self.ocupation = ocupation
        self.id_league = id_league
        # manual
        self.columns = [
            'id_user', 'id_league', 'name', 'last_name', 'last_last_name',
            'city', 'suburb', 'street', 'no', 'phone', 'email', 'password', 'job']

    def valid_user(self, sql):
        if sql.read('Usr', ['*'], "email='{}'".format(self.email)) == []:
            return False
        else:
            return True

    def valid_password(self, sql):

        response = sql.read('Usr', ['*'], "email='{}' and password='{}'".format(self.email, self.password))
        print("Response:", response)

        if response == [] or response is None:
            return False
        else:
            self.fill_data(response[0])
            return True

    def add(self, sql):
        # nombre de la tabla, id
        self.id_user = sql.next_ID('Usr', 'id_user') + 1

        args = [
            str(self.id_user), str(self.id_league), self.name, self.last_name, self.last_last_name,
            self.city, self.suburb, self.street, str(self.no), self.phone, self.email, self.password, self.ocupation
        ]
        # create(Nombre de la tabla, ...)
        sql.create('Usr', self.columns, args)
        sql.commit()

    def delete(self, sql):

        sql.delete('Usr', 'id_user={}'.format(self.id_user))
        sql.commit()

    def update(self, sql, old=None):
        if old is None:
            old = self.email
        args = [
            str(self.id_user), str(self.id_league), self.name, self.last_name, self.last_last_name,
            self.city, self.suburb, self.street, str(self.no), self.phone, self.email, self.password, self.ocupation
        ]
        sql.update('Usr', self.columns, args, "email='{}'".format(old))
        sql.commit()

    def fill_data(self, data):
        self.id_user = data[0]
        self.id_league = data[1]
        self.name = data[2]
        self.last_name = data[3]
        self.last_last_name = data[4]
        self.city = data[5]
        self.suburb = data[6]
        self.street = data[7]
        self.no = data[8]
        self.phone = data[9]
        self.ocupation = data[12]


class Player:
    """docstring for Player"""

    def __init__(self, id_player='', name='', last_name='',
                 last_last_name='', curp='', city='', suburb='',
                 street='', no='0', id_team='1', expulsions='0',
                 reprimands='0', goals='0', appearances='0'):
        self.id_player = id_player
        self.name = name
        self.last_name = last_name
        self.last_last_name = last_last_name
        self.curp = curp
        self.city = city
        self.suburb = suburb
        self.street = street
        self.no = no
        self.id_team = id_team
        self.expulsions = expulsions
        self.reprimands = reprimands
        self.goals = goals
        self.appearances = appearances

        self.columns = [
            'id_player', 'name', 'last_name', 'last_last_name', 'curp',
            'city', 'suburb', 'street', 'no', 'id_team', 'expulsions', 'reprimands',
            'goals', 'appearances'
        ]

    def valid_curp(self, sql):
        if sql.read('Player', ['*'], "curp='{}'".format(self.curp)) == []:
            return False
        else:
            return True

    def get_team(self, sql):
        return sql.read('Team', ["name"], "id_team={}".format(self.id_team))[0][0]

    def add(self, sql):
        # nombre de la tabla, id
        self.id_player = sql.next_ID('Player', 'id_player') + 1

        args = [
            self.id_player, self.name, self.last_name, self.last_last_name,
            self.curp, self.city, self.suburb, self.street, self.no, self.id_team, self.expulsions,
            self.reprimands, self.goals, self.appearances
        ]
        sql.create('Player', self.columns, args)
        sql.commit()

    def delete(self, sql):
        sql.delete('Player', 'id_player={}'.format(self.id_player))
        sql.commit()

    def update_statistics(self, sql, appearence, goals, reprimand, expulsion):
        query = "UPDATE Player \nSET "
        query += "expulsions = expulsions + {}, ".format(expulsion)
        query += "reprimands = reprimands + {}, ".format(reprimand)
        query += "appearances = appearances + {}, ".format(appearence)
        query += "goals = goals + {}\n".format(goals)
        query += "WHERE name='{}' AND last_name='{}' AND last_last_name='{}'".format(self.name, self.last_name,
                                                                                     self.last_last_name)
        sql.query(query)

    def update(self, sql):
        args = [
            self.id_player, self.name, self.last_name, self.last_last_name,
            self.curp, self.city, self.suburb, self.street, self.no, self.id_team, self.expulsions,
            self.reprimands, self.goals, self.appearances
        ]
        sql.update('Player', self.columns, args, 'id_player={}'.format(self.id_player))
        sql.commit()


class League:
    """docstring for League"""

    def __init__(self, id_league='', name=''):
        super(League, self).__init__()
        self.id_league = id_league
        self.name = name
        self.columns = ['id_league', 'name']

    def get_tournaments(self, sql):
        response = sql.read('Tournament', ['name'], "id_league={}".format(self.id_league))
        if response == []:
            return [['']]
        else:
            return response

    def add(self, sql):
        # nombre de la tabla, id
        self.id_league = sql.next_ID('League', 'id_league') + 1

        args = [self.id_league, self.name]

        # create(Nombre de la tabla, ...)
        sql.create('League', self.columns, args)
        sql.commit()

    def delete(self, sql):

        sql.delete('League', 'id_league={}'.format(self.id_league))
        sql.commit()

    def update(self, sql):
        args = [self.id_league, self.name]
        sql.update('League', self.columns, args, 'id_league={}'.format(self.id_league))
        sql.commit()


class Tournament:
    """docstring for Tournament"""

    def __init__(self, name='', season='', id_tournament='', id_league='1'):
        self.id_tournament = id_tournament
        self.name = name
        self.season = season
        self.id_league = id_league

        self.columns = ['id_tournament', 'name', 'season', 'id_league']

    def add(self, sql):
        # nombre de la tabla, id
        self.id_tournament = sql.next_ID('Tournament', 'id_tournament') + 1
        args = [self.id_tournament, self.name, self.season, self.id_league]
        # create(Nombre de la tabla, ...)
        sql.create('Tournament', self.columns, args)
        sql.commit()

    def delete(self, sql):
        sql.delete('Tournament', 'id_tournament={}'.format(self.id_tournament))
        sql.commit()

    def update(self, sql):
        args = [self.id_tournament, self.name, self.season, self.id_league]
        sql.update('Tournament', self.columns, args, 'id_tournament={}'.format(self.id_tournament))
        sql.commit()


class Team:
    """docstring for Team"""

    def __init__(self, name='', short_name='',
                 local_place='', id_team='', id_dt='', goals=0, goals_conceded=0, win=0, lost=0, draw=0):
        self.id_team = id_team
        self.name = name
        self.short_name = short_name
        self.local_place = local_place
        self.id_dt = id_dt
        self.goals = goals
        self.goals_conceded = goals_conceded
        self.win = win
        self.lost = lost
        self.draw = draw
        self.columns = ['id_team', 'name', 'nick_name', 'local_place', 'id_dt', 'goals', 'goals_conceded', 'win',
                        'lost', 'draw']
        self.args = None

    def get_players(self, sql):
        return sql.read("Player", ["curp", "name", "last_name", "last_last_name", "city"],
                        "id_team = '{}'".format(self.id_team))

    def get_dt(self, sql):
        return sql.read("User", ["*"], "id_user = '{}'".format(self.id_dt))

    def __refresh_args(self):
        self.args = [self.id_team, self.name, self.short_name, self.local_place, self.id_dt, self.goals,
                     self.goals_conceded, self.win, self.lost, self.draw]

    def add(self, sql):
        # nombre de la tabla, id
        self.id_team = sql.next_ID('Team', 'id_team') + 1
        self.__refresh_args()
        # create(Nombre de la tabla, ...)
        sql.create('Team', self.columns, self.args)
        sql.commit()

    def delete(self, sql):
        sql.delete('Team', "id_team={} or name='{}'".format(self.id_team, self.name))
        sql.commit()

    def update_statistics(self, sql, id_tournament, goals, goals_conceded, win, lost, draw):
        query = "UPDATE DetailTournament\n"
        query += "SET "
        query += "win = win + {}, ".format(win)
        query += "lost = lost + {}, ".format(lost)
        query += "draw = draw + {}, ".format(draw)
        query += "goals = goals + {}, ".format(goals)
        query += "goals_conceded = goals_conceded + {}\n".format(goals_conceded)
        query += "WHERE id_team={} and id_tournament={}".format(self.id_team, id_tournament)
        sql.query(query)

    def update(self, sql):
        self.__refresh_args()
        sql.update('Team', self.columns, self.args, 'id_team={}'.format(self.id_team))
        sql.commit()


class Match:
    """docstring for Match"""

    def __init__(self, id_match='', place='',
                 match_date='', hour='', id_local='', id_visit='', id_day='', id_referee='', g_local='0',
                 g_visit='0'):
        self.id_match = id_match
        self.place = place
        self.g_local = g_local
        self.g_visit = g_visit
        self.match_date = match_date
        self.hour = hour
        self.id_local = id_local
        self.id_visit = id_visit
        self.id_day = id_day
        self.id_referee = id_referee
        self.columns = [
            'id_match', 'place', 'match_date', 'hour', 'id_local', 'id_day', 'idreferee', 'id_visit', 'goals_local',
            'goals_visit'
        ]

    def add(self, sql):
        # nombre de la tabla, id
        self.id_match = sql.next_ID('Match', 'id_match') + 1

        args = [
            self.id_match, self.place, self.match_date,
            self.hour, self.id_local, self.id_day, self.id_referee, self.id_visit, self.g_local, self.g_visit
        ]

        # create(Nombre de la tabla, ...)
        sql.create('Match', self.columns, args)
        sql.commit()

    def delete(self, sql):
        sql.delete('Match', 'id_match={}'.format(self.id_match))
        sql.commit()

    def update(self, sql):
        args = [
            self.id_match, self.place, self.match_date,
            self.hour, self.id_local, self.id_day, self.id_referee, self.id_visit, self.g_local, self.g_visit
        ]
        sql.update('Match', self.columns, args, 'id_match={}'.format(self.id_match))
        sql.commit()


class Day:
    """docstring for Day"""

    def __init__(self, id_day='', id_tournament=''):
        super(Day, self).__init__()
        self.id_day = id_day
        self.id_tournament = id_tournament
        self.columns = [
            'id_day', 'id_tournament'
        ]

    def add(self, sql):
        # nombre de la tabla, id
        self.id_day = sql.next_ID('Day', 'id_day') + 1

        args = [
            self.id_day, self.id_tournament
        ]
        # create(Nombre de la tabla, ...)
        sql.create('Day', self.columns, args)
        sql.commit()

    def delete(self, sql):
        sql.delete('Day', 'id_day={}'.format(self.id_day))
        sql.commit()

    def update(self, sql):
        args = [
            self.id_day, self.id_tournament
        ]
        sql.update('Day', self.columns, args, 'id_day={}'.format(self.id_day))
        sql.commit()


class DetailTournament:
    """docstring for DetailTournament"""

    def __init__(self, id_tournament='', id_team='', win=0, lost=0, draw=0, goals=0, goals_conceded=0):
        self.id_tournament = id_tournament
        self.id_team = id_team
        self.win = win
        self.lost = lost
        self.draw = draw
        self.goals = goals
        self.goals_conceded = goals_conceded
        self.columns = [
            'id_tournament', 'id_team', 'win', 'lost', 'draw', 'goals', 'goals_conceded'
        ]

    def add(self, sql):
        # nombre de la tabla, id
        args = [
            self.id_tournament, self.id_team, self.win, self.lost, self.draw, self.goals, self.goals_conceded
        ]
        # create(Nombre de la tabla, ...)
        sql.create('DetailTournament', self.columns, args)
        sql.commit()

    def delete(self, sql):
        sql.delete('DetailTournament', 'id_detail={}'.format(self.id_detail))
        sql.commit()

    def update(self, sql):
        args = [
            self.id_tournament, self.id_team, self.win, self.lost, self.draw, self.goals, self.goals_conceded
        ]
        sql.update('DetailTournament', self.columns, args,
                   'id_team={} and id_tournament={}'.format(self.id_team, self.id_tournament))
        sql.commit()
