class User():
    """docstring for User"""

    def __init__(self, email='None', password='None', name='None',
                 last_name='None', last_last_name='None', city='None', suburb='None',
                 street='None', no=0, phone='None', ocupation='admin', id_user=0, id_league='1'):
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
            'city', 'suburb', 'street', 'no', 'phone', 'email', 'password', 'job'
        ]

    def valid_user(self, sql):
        response = sql.read('Usr', ['*'], "email='{}'".format(self.email))
        print("Response:", response)
        if response == []:
            return False
        else:
            return True

    def valid_password(self, sql):

        response = sql.read('Usr', ['*'], "email='{}' and password='{}'".format(self.email, self.password))
        print("Response:", response)

        if response == []:
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

    def update(self, sql):
        args = [
            self.id_user, self.id_league, self.name, self.last_name, self.last_last_name,
            self.city, self.suburb, self.street, self.no, self.phone, self.email, self.password, self.ocupation
        ]
        sql.update('Usr', self.columns, args, "email='{}'".format(self.email))
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


class Player():
    """docstring for Player"""

    def __init__(self, id_player='', name='', last_name='',
                 last_last_name='', CURP='', city='', suburb='',
                 street='', no=''):
        self.id_player = id_player
        self.name = name
        self.last_name = last_name
        self.last_last_name = last_last_name
        self.CURP = CURP
        self.city = city
        self.suburb = suburb
        self.street = street
        self.no = no


class League():
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


class Tournament():
    """docstring for Tournament"""

    def __init__(self, name='', season='', id_tournament='', id_league=''):
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


class Team():
    """docstring for Team"""

    def __init__(self, name='', short_name='',
                 local_place='', id_team='', id_dt=''):
        self.id_team = id_team
        self.name = name
        self.short_name = short_name
        self.local_place = local_place
        self.id_dt = id_dt
        self.columns = ['id_team', 'name', 'nick_name', 'local_place', 'id_dt']
        self.args = None

    def refresh_args(self):
        self.args = [self.id_team, self.name, self.short_name, self.local_place, self.id_dt]

    def add(self, sql):
        # nombre de la tabla, id
        self.id_team = sql.next_ID('Team', 'id_team') + 1
        self.refresh_args()
        # create(Nombre de la tabla, ...)
        sql.create('Team', self.columns, self.args)
        sql.commit()

    def delete(self, sql):
        sql.delete('Team', "id_team={} or name='{}'".format(self.id_team, self.name))
        sql.commit()

    def update(self, sql):
        self.refresh_args()
        sql.update('Team', self.columns, self.args, 'id_team={}'.format(self.id_team))
        sql.commit()

    class DetailTournament():
        """docstring for DetailTournament"""
        def __init__(self, id_detail=0, id_tournament=0, id_team=0):
            self.id_detail = id_detail
            self.id_tournament = id_tournament
            self.id_team = id_team
            self.columns = ['id_detail', 'id_tournament', 'id_team']

        def add(self, sql):
            # nombre de la tabla, id
            self.id_detail = sql.next_ID('DetailTournament', 'id_detail') + 1
            args = [self.id_detail, self.id_tournament, self.id_team]
            # create(Nombre de la tabla, ...)
            sql.create('DetailTournament', self.columns, args)
            sql.commit()

        def delete(self, sql):
            sql.delete('DetailTournament', 'id_detail={}'.format(self.id_detail))
            sql.commit()

        def update(self, sql):
            args = [self.id_detail, self.id_tournament, self.id_team]
            sql.update('DetailTournament', self.columns, args, 'id_detail={}'.format(self.id_detail))
            sql.commit()