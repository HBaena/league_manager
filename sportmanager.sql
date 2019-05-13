/* SCRIPT DE LA BASE DE DATOS */
Create database TeamManager
USE TeamManager

create table Player
(
    id_player int primary key,
    name varchar(30),
    last_name varchar(30),
    last_last_ame varchar(30),
    curp varchar(20),
    city varchar(30),
    suburb varchar(30),
    street varchar(30),
    no int,
    id_team int,
    expulsions int,
    reprimands int,
    goals int,
    appearances int
);
create table Usr
(
    id_user int primary key,
    id_league int,
    name varchar(30),
    last_name varchar(30),
    last_last_name varchar(30),
    city varchar(30),
    suburb varchar(30),
    street varchar(30),
    no int,
    phone int,
    email varchar(30),
    password varchar(30),
    job varchar(30)
);
create table League
(
    id_league int primary key,
    name varchar(50)
);
create table Team(
    id_team int primary key,
    name varchar(30),
    nick_name varchar(50),
    local_place varchar(50),
    id_dt int
);

create table Tournament(
    id_tournament int primary key,
    name varchar(50),
    season varchar(50),
    id_league int
    );

create table Day(
    id_day int primary key,
    id_tournament int
    );

create table Match(
    id_match int primary key,
    visitor int,
    local int,
    place varchar(30),
    match_date date,
    hour TIME,
    id_local int,
    id_day int,
    Idreferee int,
    );

create table DetailTournament(
    id_detail int,
    id_tournament int,
    id_team int
    );