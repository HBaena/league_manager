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
        self.id_user = sql.next_ID('Usr', 'id_user') + 1

        args = [
            self.id_user, self.id_league, self.name, self.last_name, self.last_last_name,
            self.city, self.suburb, self.street, self.no, self.phone, self.email, self.password, self.ocupation
        ]
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
        sql.update('Usr', self.columns, args, 'id_user={}'.format(self.id_user))
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
        self.id_name = name

    def get_tournaments(self, sql):
        response = sql.read('Tournament', ['name'], "id_league={}".format(self.id_league))
        if response == []:
            return [['']]
        else:
            return response


class Tournament():
    """docstring for Tournament"""

    def __init__(self, id_tournament='', id_league='', name='', season=''):
        super(Tournament, self).__init__()
        self.id_tournament = id_tournament
        self.id_league = id_league
        self.name = name
        self.season = season
